# Shemsu Shop — Kotlin Code for Menu (Categories & Sub-Items)

---

## Menu Data Structure

The `menu` table uses a **self-referencing parent** pattern:

```
menu table
┌─────┬──────────────────┬───────┬──────────┐
│ id  │ name             │ price │ parent   │
├─────┼──────────────────┼───────┼──────────┤
│ 1   │ Breakfast        │ 0.0   │ NULL     │  ← CATEGORY (price=0, not orderable)
│ 2   │ Main Dishes      │ 0.0   │ NULL     │  ← CATEGORY
│ 3   │ Drinks           │ 0.0   │ NULL     │  ← CATEGORY
│ 4   │ Fetira           │ 160.0 │ Breakfast│  ← SUB-ITEM (price>0, orderable)
│ 5   │ Chechebsa        │ 150.0 │ Breakfast│  ← SUB-ITEM
│ 6   │ Burger           │ 200.0 │ Main     │  ← SUB-ITEM
│ 7   │ Pizza            │ 350.0 │ Main     │  ← SUB-ITEM
│ 8   │ Pepsi            │ 50.0  │ Drinks   │  ← SUB-ITEM
│ 9   │ Water            │ 30.0  │ Drinks   │  ← SUB-ITEM
└─────┴──────────────────┴───────┴──────────┘

Rules:
- price = 0.0  → CATEGORY (parent is NULL, not clickable to order, shows ▶️)
- price > 0    → SUB-ITEM (parent points to category name, orderable)
- parent = null → top-level category
```

**API endpoint:** `GET /api/menu` returns ALL items flat. The app builds the tree.

---

## File: `data/repository/MenuRepository.kt`

```kotlin
package com.shemshop.data.repository

import com.shemshop.data.model.MenuItemDto
import com.shemshop.data.remote.ApiService
import com.shemshop.data.remote.RetrofitClient

/**
 * Fetches menu data from the backend API.
 *
 * The API returns ALL menu items in a flat list.
 * This repository provides helpers to organize them into categories and sub-items.
 *
 * ALTERNATIVE: For faster loading, the app can read directly from Supabase:
 *
 *   implementation("io.github.jan-tennert.supabase:postgrest-kt:2.6.0")
 *
 *   val client = createSupabaseClient(
 *       supabaseUrl = "https://[your-project].supabase.co",
 *       supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
 *   ) { install(Postgrest) }
 *
 *   suspend fun getMenuDirect(): List<MenuItemDto> {
 *       return client.from("menu")
 *           .select()
 *           .decodeList<MenuItemDto>()
 *   }
 *
 * Both approaches return the same data. The API route is preferred because
 * it doesn't expose the Supabase anon key in the app. Use Supabase direct only
 * if you understand the security implications.
 */
class MenuRepository(
    private val api: ApiService = RetrofitClient.api
) {

    /**
     * Fetch all menu items from the API.
     */
    suspend fun getAllItems(): Result<List<MenuItemDto>> {
        return try {
            val response = api.getMenu()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to load menu"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get only top-level categories (parent = null, not categories themselves).
     * Categories are items where price = 0.0.
     */
    fun getCategories(allItems: List<MenuItemDto>): List<MenuItemDto> {
        return allItems
            .filter { it.parent == null }
            .sortedBy { it.name }
    }

    /**
     * Get sub-items for a given category name.
     * Sub-items are items whose parent field matches the category name.
     */
    fun getSubItems(allItems: List<MenuItemDto>, categoryName: String): List<MenuItemDto> {
        return allItems
            .filter { it.parent == categoryName && it.price > 0 }
            .sortedBy { it.name }
    }

    /**
     * Check if a category has sub-items (used to show ▶️ indicator).
     */
    fun hasSubItems(allItems: List<MenuItemDto>, categoryName: String): Boolean {
        return allItems.any { it.parent == categoryName }
    }

    /**
     * Search items by name (case-insensitive).
     * Searches both category names and sub-item names.
     */
    fun search(allItems: List<MenuItemDto>, query: String): List<MenuItemDto> {
        if (query.isBlank()) return allItems
        val q = query.lowercase()
        return allItems.filter { it.name.lowercase().contains(q) }
    }
}
```

---

## File: `viewmodel/MenuViewModel.kt`

```kotlin
package com.shemshop.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shemshop.data.model.MenuItemDto
import com.shemshop.data.repository.MenuRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

/**
 * Possible states for the menu screen.
 */
sealed class MenuState {
    object Loading : MenuState()
    data class Loaded(
        val allItems: List<MenuItemDto>,
        val categories: List<MenuItemDto>,
        val selectedCategory: String?,
        val displayedItems: List<MenuItemDto>,
        val searchQuery: String
    ) : MenuState()
    data class Error(val message: String) : MenuState()
}

class MenuViewModel(
    private val menuRepository: MenuRepository = MenuRepository()
) : ViewModel() {

    private val _menuState = MutableStateFlow<MenuState>(MenuState.Loading)
    val menuState: StateFlow<MenuState> = _menuState

    private val _cartCount = MutableStateFlow(0)
    val cartCount: StateFlow<Int> = _cartCount

    init {
        loadMenu()
    }

    /**
     * Fetch menu from API.
     */
    fun loadMenu() {
        _menuState.value = MenuState.Loading
        viewModelScope.launch {
            val result = menuRepository.getAllItems()
            _menuState.value = if (result.isSuccess) {
                val items = result.getOrThrow()
                val categories = menuRepository.getCategories(items)
                MenuState.Loaded(
                    allItems = items,
                    categories = categories,
                    selectedCategory = null,
                    displayedItems = items.filter { it.price > 0 || it.parent == null },
                    searchQuery = ""
                )
            } else {
                MenuState.Error(
                    result.exceptionOrNull()?.message ?: "Failed to load menu"
                )
            }
        }
    }

    /**
     * Select a category chip.
     * null = show all items (categories + sub-items).
     * "Breakfast" = show only Breakfast sub-items.
     */
    fun selectCategory(categoryName: String?) {
        val state = _menuState.value
        if (state !is MenuState.Loaded) return

        val displayed = if (categoryName == null) {
            // Show all: categories + all sub-items
            state.allItems.filter { it.price > 0 || it.parent == null }
        } else {
            // Show sub-items for this category only
            menuRepository.getSubItems(state.allItems, categoryName)
        }

        _menuState.value = state.copy(
            selectedCategory = categoryName,
            displayedItems = displayed,
            searchQuery = ""
        )
    }

    /**
     * Search items by name.
     */
    fun search(query: String) {
        val state = _menuState.value
        if (state !is MenuState.Loaded) return

        val filtered = menuRepository.search(state.allItems, query)
        _menuState.value = state.copy(
            searchQuery = query,
            selectedCategory = null,
            displayedItems = filtered
        )
    }

    /**
     * Update cart badge count (called from CartViewModel).
     */
    fun updateCartCount(count: Int) {
        _cartCount.value = count
    }
}
```

---

## File: `ui/screens/menu/MenuScreen.kt`

```kotlin
package com.shemshop.ui.screens.menu

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shemshop.data.model.MenuItemDto
import com.shemshop.viewmodel.MenuState
import com.shemshop.viewmodel.MenuViewModel

/**
 * Menu screen with:
 * - Search bar at top
 * - Category chips (horizontal scroll)
 * - Items grid (2 columns)
 * - Cart FAB with badge
 *
 * Categories (price=0.0, parent=null) show as chips.
 * Sub-items (price>0, parent="CategoryName") show as orderable cards.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MenuScreen(
    viewModel: MenuViewModel,
    onCartClick: () -> Unit,
    onAddToCart: (MenuItemDto) -> Unit
) {
    val menuState by viewModel.menuState.collectAsState()
    val cartCount by viewModel.cartCount.collectAsState()

    var searchQuery by remember { mutableStateOf("") }
    var showSearch by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    if (showSearch) {
                        OutlinedTextField(
                            value = searchQuery,
                            onValueChange = {
                                searchQuery = it
                                viewModel.search(it)
                            },
                            placeholder = { Text("Search menu...") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                unfocusedBorderColor = MaterialTheme.colorScheme.surface
                            )
                        )
                    } else {
                        Text("Menu")
                    }
                },
                actions = {
                    IconButton(onClick = {
                        showSearch = !showSearch
                        if (!showSearch) {
                            searchQuery = ""
                            viewModel.search("")
                        }
                    }) {
                        Icon(Icons.Default.Search, contentDescription = "Search")
                    }
                }
            )
        },
        floatingActionButton = {
            if (cartCount > 0) {
                FloatingActionButton(
                    onClick = onCartClick,
                    containerColor = MaterialTheme.colorScheme.primary
                ) {
                    BadgedBox(badge = {
                        Badge { Text("$cartCount") }
                    }) {
                        Icon(Icons.Default.ShoppingCart, contentDescription = "Cart")
                    }
                }
            }
        }
    ) { padding ->
        when (val state = menuState) {
            is MenuState.Loading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            is MenuState.Error -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = state.message,
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { viewModel.loadMenu() }) {
                            Text("Retry")
                        }
                    }
                }
            }

            is MenuState.Loaded -> {
                Column(modifier = Modifier.padding(padding)) {
                    // --- Category Chips ---
                    CategoryChipsRow(
                        categories = state.categories,
                        selectedCategory = state.selectedCategory,
                        onCategorySelected = { viewModel.selectCategory(it) }
                    )

                    HorizontalDivider(thickness = 0.5.dp)

                    // --- Items Grid ---
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(12.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // If showing "All" (no category selected) and not searching,
                        // show category headers with their sub-items grouped
                        if (state.selectedCategory == null && state.searchQuery.isBlank()) {
                            items(state.categories) { category ->
                                CategoryGroup(
                                    category = category,
                                    subItems = state.allItems.filter {
                                        it.parent == category.name && it.price > 0
                                    },
                                    onAddToCart = onAddToCart
                                )
                            }
                        } else {
                            // Show filtered items as flat grid
                            items(state.displayedItems) { item ->
                                if (item.price > 0) {
                                    MenuItemCard(
                                        item = item,
                                        onAddToCart = onAddToCart
                                    )
                                }
                            }
                        }
                    }

                    // --- Other / Custom Request Card ---
                    if (state.selectedCategory == null && state.searchQuery.isBlank()) {
                        OtherRequestCard(
                            onRequest = {
                                // Navigate to custom item input screen
                            }
                        )
                    }
                }
            }
        }
    }
}

/**
 * Horizontal scrollable row of category chips.
 * First chip is always "All" (shows everything).
 */
@Composable
private fun CategoryChipsRow(
    categories: List<MenuItemDto>,
    selectedCategory: String?,
    onCategorySelected: (String?) -> Unit
) {
    LazyRow(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item {
            FilterChip(
                selected = selectedCategory == null,
                onClick = { onCategorySelected(null) },
                label = { Text("All") }
            )
        }
        items(categories) { category ->
            FilterChip(
                selected = selectedCategory == category.name,
                onClick = { onCategorySelected(category.name) },
                label = { Text(category.name) }
            )
        }
    }
}

/**
 * A category header followed by its sub-items.
 * Used in the "All" view (no category selected).
 */
@Composable
private fun CategoryGroup(
    category: MenuItemDto,
    subItems: List<MenuItemDto>,
    onAddToCart: (MenuItemDto) -> Unit
) {
    Column {
        Text(
            text = category.name,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(vertical = 8.dp, horizontal = 4.dp)
        )
        subItems.forEach { item ->
            MenuItemCard(
                item = item,
                onAddToCart = onAddToCart,
                modifier = Modifier.padding(start = 8.dp)
            )
        }
    }
}

/**
 * A single orderable menu item card.
 * Shows: name, price, add-to-cart button.
 */
@Composable
private fun MenuItemCard(
    item: MenuItemDto,
    onAddToCart: (MenuItemDto) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.name,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Birr ${item.price}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // "Add +" button — opens quantity selector in a bottom sheet
            FilledTonalButton(
                onClick = { onAddToCart(item) },
                modifier = Modifier.height(36.dp),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 0.dp)
            ) {
                Icon(
                    Icons.Default.Add,
                    contentDescription = "Add",
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("Add", fontSize = 14.sp)
            }
        }
    }
}

/**
 * "Other ✏️" card at the bottom — for custom item requests.
 */
@Composable
private fun OtherRequestCard(
    onRequest: () -> Unit
) {
    Card(
        onClick = onRequest,
        modifier = Modifier
            .fillMaxWidth()
            .padding(12.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Other ✏️",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.weight(1f)
            )
            Text(
                text = "Tap to describe what you want",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSecondaryContainer
            )
        }
    }
}
```

---

## File: `ui/screens/menu/AddToCartSheet.kt`

```kotlin
package com.shemshop.ui.screens.menu

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shemshop.data.model.MenuItemDto

/**
 * Bottom sheet shown when user taps "Add" on a menu item.
 * Allows selecting quantity before adding to cart.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddToCartSheet(
    item: MenuItemDto,
    onConfirm: (qty: Int) -> Unit,
    onDismiss: () -> Unit
) {
    var qty by remember { mutableIntStateOf(1) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Item name
            Text(
                text = item.name,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Price
            Text(
                text = "Birr ${item.price}",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Quantity stepper
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                IconButton(
                    onClick = { if (qty > 1) qty-- },
                    enabled = qty > 1
                ) {
                    Icon(Icons.Default.Remove, contentDescription = "Decrease")
                }

                Text(
                    text = "$qty",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.width(48.dp),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )

                IconButton(
                    onClick = { if (qty < 99) qty++ },
                    enabled = qty < 99
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Increase")
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Total for this line
            Text(
                text = "Total: Birr ${"%.2f".format(item.price * qty)}",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Add to Cart button
            Button(
                onClick = { onConfirm(qty) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text(
                    text = "Add to Cart ($qty)",
                    fontSize = 16.sp
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
```

---

## File: `util/MenuExtensions.kt`

```kotlin
package com.shemshop.util

import com.shemshop.data.model.MenuItemDto

/**
 * Extension functions for organizing menu data.
 */
object MenuExtensions {

    /**
     * Check if an item is a category (not directly orderable).
     * Categories have price = 0.0 and parent = null.
     */
    fun MenuItemDto.isCategory(): Boolean {
        return this.price == 0.0 && this.parent == null
    }

    /**
     * Check if an item is a sub-item (directly orderable).
     * Sub-items have price > 0 and a non-null parent.
     */
    fun MenuItemDto.isSubItem(): Boolean {
        return this.price > 0.0 && this.parent != null
    }

    /**
     * Check if a category has any sub-items in the full list.
     */
    fun hasChildren(categoryName: String, allItems: List<MenuItemDto>): Boolean {
        return allItems.any { it.parent == categoryName }
    }

    /**
     * Get all sub-items for a category, sorted by name.
     */
    fun getChildren(categoryName: String, allItems: List<MenuItemDto>): List<MenuItemDto> {
        return allItems
            .filter { it.parent == categoryName && it.price > 0 }
            .sortedBy { it.name }
    }

    /**
     * Build a map of category → list of sub-items for the "All" view.
     */
    fun groupByCategory(allItems: List<MenuItemDto>): Map<MenuItemDto, List<MenuItemDto>> {
        val categories = allItems.filter { it.isCategory() }.sortedBy { it.name }
        val result = linkedMapOf<MenuItemDto, List<MenuItemDto>>()
        for (cat in categories) {
            val children = getChildren(cat.name, allItems)
            if (children.isNotEmpty()) {
                result[cat] = children
            }
        }
        return result
    }
}
```

---

## File: `data/model/CartItem.kt`

```kotlin
package com.shemshop.data.model

/**
 * Represents an item in the user's shopping cart.
 * This is local state only — not stored on the server until order is placed.
 */
data class CartItem(
    val item: String,
    val qty: Int,
    val price: Double,
    val isCustom: Boolean = false
) {
    val lineTotal: Double get() = qty * price
}

/**
 * ViewModel for managing cart state.
 * Cart is stored locally in memory (MutableStateFlow).
 * When user checks out, cart contents are sent to the API.
 */
data class CartState(
    val items: List<CartItem> = emptyList(),
    val comment: String = ""
) {
    val subtotal: Double get() = items.sumOf { it.lineTotal }
    val itemCount: Int get() = items.sumOf { it.qty }
    val isEmpty: Boolean get() = items.isEmpty()
}
```

---

## File: `viewmodel/CartViewModel.kt`

```kotlin
package com.shemshop.viewmodel

import androidx.lifecycle.ViewModel
import com.shemshop.data.model.CartItem
import com.shemshop.data.model.CartState
import com.shemshop.data.model.MenuItemDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class CartViewModel : ViewModel() {

    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState

    /**
     * Add a menu item to cart (or increase quantity if already present).
     */
    fun addItem(item: MenuItemDto, qty: Int = 1) {
        val current = _cartState.value.items.toMutableList()
        val existing = current.indexOfFirst { it.item == item.name }
        if (existing >= 0) {
            current[existing] = current[existing].copy(qty = current[existing].qty + qty)
        } else {
            current.add(CartItem(item = item.name, qty = qty, price = item.price))
        }
        _cartState.value = _cartState.value.copy(items = current)
    }

    /**
     * Remove an item from cart entirely.
     */
    fun removeItem(itemName: String) {
        val current = _cartState.value.items.filter { it.item != itemName }
        _cartState.value = _cartState.value.copy(items = current)
    }

    /**
     * Update quantity for an item (set to 0 to remove).
     */
    fun updateQty(itemName: String, qty: Int) {
        if (qty <= 0) {
            removeItem(itemName)
            return
        }
        val current = _cartState.value.items.toMutableList()
        val index = current.indexOfFirst { it.item == itemName }
        if (index >= 0) {
            current[index] = current[index].copy(qty = qty)
            _cartState.value = _cartState.value.copy(items = current)
        }
    }

    /**
     * Set order comment / special instructions.
     */
    fun setComment(comment: String) {
        _cartState.value = _cartState.value.copy(comment = comment)
    }

    /**
     * Clear the entire cart (after successful checkout).
     */
    fun clearCart() {
        _cartState.value = CartState()
    }
}
```

---

## How the Menu Flow Works End to End

```
┌──────────────────────────────────────────────────────────┐
│                     MENU SCREEN                           │
│                                                           │
│  App launch → MenuViewModel.loadMenu()                    │
│       ↓                                                   │
│  MenuRepository.getAllItems()                              │
│       ↓                                                   │
│  GET /api/menu → returns flat JSON array:                 │
│  [                                                        │
│    { "id":1,"name":"Breakfast","price":0,"parent":null }, │
│    { "id":4,"name":"Fetira","price":160,"parent":"Brkfst"},│
│    ...                                                     │
│  ]                                                        │
│       ↓                                                   │
│  ViewModel builds:                                         │
│    - categories = filter(price=0 AND parent=null)          │
│    - subItems  = filter(price>0 AND parent="Category")     │
│       ↓                                                   │
│  Screen displays:                                          │
│    ┌─────────────────────────────────────────┐             │
│    │ [All] [Breakfast] [Main] [Drinks] ...   │ ← chips     │
│    ├─────────────────────────────────────────┤             │
│    │ Breakfast                               │             │
│    │  ┌──────────────────────────────────┐   │             │
│    │  │ Fetira          Birr 160  [Add+] │   │             │
│    │  │ Chechebsa       Birr 150  [Add+] │   │             │
│    │  └──────────────────────────────────┘   │             │
│    │ Main Dishes                             │             │
│    │  ┌──────────────────────────────────┐   │             │
│    │  │ Burger          Birr 200  [Add+] │   │             │
│    │  │ Pizza           Birr 350  [Add+] │   │             │
│    │  └──────────────────────────────────┘   │             │
│    │ ...                                     │             │
│    │  ┌──────────────────────────────────┐   │             │
│    │  │ Other ✏️  Tap to describe...     │   │             │
│    │  └──────────────────────────────────┘   │             │
│    └─────────────────────────────────────────┘             │
│                                                           │
│  User taps "Add+" on Fetira → AddToCartSheet opens         │
│       ↓                                                   │
│  User selects qty=4 → taps "Add to Cart (4)"               │
│       ↓                                                   │
│  CartViewModel.addItem(Fetira, 4)                          │
│       ↓                                                   │
│  MenuViewModel.cartCount updates → FAB badge shows "4"    │
│                                                           │
│  User taps category chip "Breakfast" →                     │
│    ViewModel.selectCategory("Breakfast")                    │
│    Only Fetira, Chechebsa shown                            │
│                                                           │
│  User taps "All" chip → all items shown again              │
└──────────────────────────────────────────────────────────┘
```
