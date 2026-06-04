package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.data.model.CartItem
import com.example.data.model.MenuItem
import com.example.data.model.OrderGroup
import com.example.viewmodel.CartViewModel
import com.example.viewmodel.DebtViewModel
import com.example.viewmodel.MenuViewModel
import com.example.viewmodel.OrdersViewModel
import com.example.ui.theme.*

// --- HOME SCREEN ---
@Composable
fun HomeScreen(
    fullName: String,
    ordersViewModel: OrdersViewModel,
    debtViewModel: DebtViewModel,
    cartViewModel: CartViewModel,
    onQuickAction: (String) -> Unit
) {
    val activeDebtTotal by debtViewModel.activeTotal.collectAsState()
    val orders by ordersViewModel.orders.collectAsState()
    val cartCount by cartViewModel.itemCount.collectAsState()

    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        // Welcome Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Hi, ${fullName.substringBefore(" ")} 👋",
                    fontFamily = FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    fontSize = 28.sp,
                    color = OnSurface
                )
                Text(
                    text = "Welcome back to the harvest.",
                    fontSize = 14.sp,
                    color = OnSurfaceVariant.copy(alpha = 0.7f),
                    modifier = Modifier.padding(top = 2.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Active Debt Card (If exists)
        if (activeDebtTotal > 0.0) {
            GlassCard(
                modifier = Modifier.fillMaxWidth().testTag("active_debt_card"),
                borderStroke = BorderStroke(2.dp, AccentGold.copy(alpha = 0.4f))
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Text(
                            text = "CURRENT STANDING",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = AccentGold,
                            letterSpacing = 1.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Active Debt",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 22.sp,
                            color = OnSurface
                        )
                    }
                    Icon(
                        imageVector = Icons.Default.AccountBalanceWallet,
                        contentDescription = "Debt wallet",
                        tint = AccentGold,
                        modifier = Modifier.size(24.dp)
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Bottom
                ) {
                    Text(
                        text = "Birr ${String.format("%.2f", activeDebtTotal)}",
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 26.sp,
                        color = OnSurface
                    )
                    Button(
                        onClick = { onQuickAction("my_debt") },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                        shape = RoundedCornerShape(20.dp),
                        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                    ) {
                        Text("Pay Now", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 13.sp)
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.Default.ArrowForward,
                            contentDescription = "Pay pointer",
                            tint = OnPrimary,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Quick Actions Grid Header
        Text(
            text = "QUICK ACTIONS",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = OnSurfaceVariant.copy(alpha = 0.5f),
            letterSpacing = 2.sp
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Action Grid 2x2
        Row(modifier = Modifier.fillMaxWidth()) {
            // Left Column
            Column(modifier = Modifier.weight(1f).padding(end = 6.dp)) {
                ActionTile(
                    title = "Order Now",
                    icon = Icons.Default.RestaurantMenu,
                    color = PrimaryOrange,
                    onClick = { onQuickAction("menu") }
                )
                Spacer(modifier = Modifier.height(12.dp))
                ActionTile(
                    title = "My Debt",
                    icon = Icons.Default.Payments,
                    color = AccentGold,
                    onClick = { onQuickAction("my_debt") }
                )
            }
            // Right Column
            Column(modifier = Modifier.weight(1f).padding(start = 6.dp)) {
                ActionTile(
                    title = "My Orders",
                    icon = Icons.Default.ReceiptLong,
                    color = SecondaryGold,
                    onClick = { onQuickAction("orders") }
                )
                Spacer(modifier = Modifier.height(12.dp))
                ActionTile(
                    title = "Help Center",
                    icon = Icons.Default.HelpOutline,
                    color = Color(0xFF91CDFF),
                    onClick = { onQuickAction("help") }
                )
            }
        }

        Spacer(modifier = Modifier.height(28.dp))

        // Recent Orders Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Recent Orders",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 22.sp,
                color = OnSurface
            )
            Text(
                text = "VIEW ALL",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = PrimaryOrange,
                modifier = Modifier.clickable { onQuickAction("orders") }
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Horizontal Recent Orders scroll
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(end = 16.dp)
        ) {
            val recents = if (orders.isEmpty()) getMockRecentOrders() else orders
            items(recents) { orderObj ->
                RecentOrderScrollCard(orderObj = orderObj)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Loyalty Card
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0x33FFD700)),
            border = BorderStroke(1.dp, AccentGold.copy(alpha = 0.15f)),
            shape = RoundedCornerShape(16.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(AccentGold.copy(alpha = 0.15f), RoundedCornerShape(8.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = "loyalty star",
                        tint = AccentGold,
                        modifier = Modifier.size(24.dp)
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "LOYALTY PROGRAM",
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = AccentGold,
                        letterSpacing = 1.sp
                    )
                    Text(
                        text = "You have 1,240 Points",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = OnSurface
                    )
                }

                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = "loyalty action",
                    tint = OnSurfaceVariant
                )
            }
        }

        Spacer(modifier = Modifier.height(80.dp)) // Extra bottom space
    }
}

@Composable
fun ActionTile(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color,
    onClick: () -> Unit
) {
    GlassCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().height(100.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(color.copy(alpha = 0.1f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = color,
                    modifier = Modifier.size(24.dp)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                color = OnSurface,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun RecentOrderScrollCard(orderObj: OrderGroup) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.width(280.dp)
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Box(modifier = Modifier.fillMaxWidth().height(128.dp)) {
                val itemName = orderObj.items.firstOrNull()?.item ?: "Dish Special"
                AsyncImage(
                    model = getFoodImageUrl(itemName),
                    contentDescription = "Food banner",
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )

                // Status tag
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(12.dp)
                        .background(
                            color = when (orderObj.status) {
                                "Delivered" -> StatusAccepted.copy(alpha = 0.85f)
                                "Ready" -> StatusReady.copy(alpha = 0.85f)
                                "Pending" -> StatusPending.copy(alpha = 0.85f)
                                else -> PrimaryContainerOrange.copy(alpha = 0.85f)
                            },
                            shape = RoundedCornerShape(12.dp)
                        )
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = orderObj.status,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }

            Column(modifier = Modifier.padding(12.dp)) {
                Text(
                    text = orderObj.items.firstOrNull()?.item ?: "Gourmet Selection",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = OnSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Order #${orderObj.order_group.take(7)}",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant.copy(alpha = 0.6f)
                    )
                    Text(
                        text = "Birr ${String.format("%.2f", orderObj.total)}",
                        fontWeight = FontWeight.Bold,
                        color = SecondaryGold,
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}

private fun getMockRecentOrders(): List<OrderGroup> {
    return listOf(
        OrderGroup("84291", null, "Delivered", emptyList(), null, null, null, 210.0),
        OrderGroup("84295", null, "Pending", emptyList(), null, null, null, 340.0),
        OrderGroup("84299", null, "Ready", emptyList(), null, null, null, 185.0)
    )
}

// --- MENU SCREEN ---
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MenuScreen(
    menuViewModel: MenuViewModel,
    cartViewModel: CartViewModel,
    onNavigateCart: () -> Unit
) {
    val categories by menuViewModel.categories.collectAsState()
    val selectedCategory by menuViewModel.selectedCategory.collectAsState()
    val filteredItems by menuViewModel.filteredItems.collectAsState()
    val cartItems by cartViewModel.cartItems.collectAsState()
    val subtotal by cartViewModel.subtotal.collectAsState()

    var showBottomSheetItem by remember { mutableStateOf<MenuItem?>(null) }
    var showOtherItemDialog by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Spacer(modifier = Modifier.height(8.dp))

            // Title Header
            Text(
                text = "Our Gourmet Menu",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 28.sp,
                color = OnSurface
            )
            Text(
                text = "Handcrafted flavors delivered with Ethiopian warmth.",
                fontSize = 14.sp,
                color = OnSurfaceVariant.copy(alpha = 0.7f),
                modifier = Modifier.padding(top = 2.dp, bottom = 16.dp)
            )

            // Category Chips Row
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
            ) {
                items(categories) { cat ->
                    val isSelected = cat == selectedCategory
                    FilterChip(
                        selected = isSelected,
                        onClick = { menuViewModel.selectCategory(cat) },
                        label = { Text(cat, fontWeight = FontWeight.Bold, fontSize = 13.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = PrimaryContainerOrange,
                            selectedLabelColor = OnPrimary,
                            containerColor = Color(0x33FFB68A),
                            labelColor = OnSurfaceVariant
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            enabled = true,
                            selected = isSelected,
                            borderColor = Color(0x11FFFFFF)
                        )
                    )
                }
            }

            // Grid of items
            if (filteredItems.isEmpty()) {
                Box(
                    modifier = Modifier.weight(1f).fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No items found in this section.",
                        color = OnSurfaceVariant.copy(alpha = 0.5f),
                        fontSize = 14.sp
                    )
                }
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier.weight(1f).fillMaxWidth(),
                    contentPadding = PaddingValues(bottom = 90.dp) // padding for floating total
                ) {
                    items(filteredItems) { item ->
                        MenuItemCard(
                            item = item,
                            onAddClick = { showBottomSheetItem = item }
                        )
                    }

                    // Special custom card at the very end
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .aspectRatio(0.8f)
                                .border(
                                    border = BorderStroke(2.dp, Brush.sweepGradient(listOf(PrimaryOrange, SecondaryGold))),
                                    shape = RoundedCornerShape(16.dp)
                                )
                                .clickable { showOtherItemDialog = true },
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center,
                                modifier = Modifier.padding(16.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(48.dp)
                                        .background(PrimaryOrange.copy(alpha = 0.1f), CircleShape),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Edit,
                                        contentDescription = "Edit special item",
                                        tint = PrimaryOrange,
                                        modifier = Modifier.size(24.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = "Other ✏️",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp,
                                    color = OnSurface
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "Special requests",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant.copy(alpha = 0.5f)
                                )
                            }
                        }
                    }
                }
            }
        }

        // Float checkout bar if cart is not empty
        if (cartItems.isNotEmpty()) {
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 76.dp, start = 16.dp, end = 16.dp)
            ) {
                Surface(
                    color = Color(0xEA1F1F1F),
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
                    tonalElevation = 6.dp,
                    modifier = Modifier.fillMaxWidth().testTag("floating_summary_bar")
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                "Current Order",
                                fontSize = 11.sp,
                                color = PrimaryOrange.copy(alpha = 0.6f),
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.5.sp
                            )
                            Text(
                                "Birr ${String.format("%.2f", subtotal)}",
                                fontFamily = FontFamily.Serif,
                                fontWeight = FontWeight.Bold,
                                fontSize = 20.sp,
                                color = OnSurface
                            )
                        }

                        Button(
                            onClick = onNavigateCart,
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                            shape = RoundedCornerShape(12.dp),
                            contentPadding = PaddingValues(horizontal = 24.dp, vertical = 12.dp)
                        ) {
                            Text("Checkout", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 15.sp)
                        }
                    }
                }
            }
        }

        // Add to Cart Bottom Sheet
        if (showBottomSheetItem != null) {
            val bItem = showBottomSheetItem!!
            var bQty by remember { mutableStateOf(1) }
            var bNote by remember { mutableStateOf("") }

            ModalBottomSheet(
                onDismissRequest = { showBottomSheetItem = null },
                containerColor = SurfaceContainerLow,
                contentColor = OnSurface
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(80.dp)
                                .clip(RoundedCornerShape(12.dp))
                        ) {
                            AsyncImage(
                                model = getFoodImageUrl(bItem.name),
                                contentDescription = bItem.name,
                                modifier = Modifier.fillMaxSize(),
                                contentScale = ContentScale.Crop
                            )
                        }

                        Column(
                            verticalArrangement = Arrangement.Center,
                            modifier = Modifier.weight(1f)
                        ) {
                            Text(
                                text = bItem.name,
                                fontWeight = FontWeight.Bold,
                                fontSize = 20.sp,
                                color = OnSurface
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Birr ${String.format("%.2f", bItem.price)}",
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                color = PrimaryOrange
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "A masterfully balanced collection of farm-fresh ingredients prepared with gourmet excellence. Customize or adjust quantity below.",
                        fontSize = 13.sp,
                        color = OnSurfaceVariant
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    // Quantity row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Quantity", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .background(Color(0xFF1E1E1E), RoundedCornerShape(20.dp))
                                .border(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f), RoundedCornerShape(20.dp))
                                .padding(horizontal = 4.dp, vertical = 2.dp)
                        ) {
                            IconButton(
                                onClick = { if (bQty > 1) bQty-- },
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(Icons.Default.Remove, contentDescription = "minus", tint = PrimaryOrange)
                            }
                            Text(
                                text = bQty.toString(),
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                modifier = Modifier.width(32.dp),
                                textAlign = TextAlign.Center
                            )
                            IconButton(
                                onClick = { bQty++ },
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(Icons.Default.Add, contentDescription = "plus", tint = PrimaryOrange)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Custom input request
                    Text(
                        text = "SPECIFIC REQUESTS",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    OutlinedTextField(
                        value = bNote,
                        onValueChange = { bNote = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Add any special request/note...", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = PrimaryOrange,
                            unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f),
                            focusedContainerColor = Color(0xFF161616),
                            unfocusedContainerColor = Color(0xFF161616)
                        ),
                        shape = RoundedCornerShape(12.dp)
                    )

                    Spacer(modifier = Modifier.height(28.dp))

                    // Total & Add Button
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("TOTAL ESTIMATE", fontSize = 10.sp, color = OnSurfaceVariant.copy(alpha = 0.6f))
                            Text(
                                "Birr ${String.format("%.2f", bItem.price * bQty)}",
                                fontFamily = FontFamily.Serif,
                                fontWeight = FontWeight.Bold,
                                fontSize = 22.sp,
                                color = OnSurface
                            )
                        }
                        Button(
                            onClick = {
                                cartViewModel.addToCart(bItem.name, bItem.price, bQty, false, bNote)
                                showBottomSheetItem = null
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                            shape = RoundedCornerShape(24.dp),
                            modifier = Modifier
                                .weight(1f)
                                .padding(start = 24.dp)
                                .height(48.dp)
                        ) {
                            Text("Add to Cart", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 15.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))
                }
            }
        }

        // Custom "Other ✏️" creation Dialog
        if (showOtherItemDialog) {
            var customName by remember { mutableStateOf("") }
            var customQty by remember { mutableStateOf(1) }
            var customPriceEstimate by remember { mutableStateOf("150.00") }

            AlertDialog(
                onDismissRequest = { showOtherItemDialog = false },
                containerColor = SurfaceContainerLow,
                title = {
                    Text(
                        "Other Custom Item ✏️",
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryOrange
                    )
                },
                text = {
                    Column(modifier = Modifier.fillMaxWidth()) {
                        Text("Tell us what you want us to prepare and we will try to make it happen!", fontSize = 13.sp, color = OnSurfaceVariant)
                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = customName,
                            onValueChange = { customName = it },
                            placeholder = { Text("What dish or drink are you requesting?", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                            label = { Text("Item Name") },
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryOrange, unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f))
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = customPriceEstimate,
                            onValueChange = { customPriceEstimate = it },
                            placeholder = { Text("Average custom price", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                            label = { Text("Target Price (Birr)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryOrange, unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f))
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Quantity", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                IconButton(onClick = { if (customQty > 1) customQty-- }) {
                                    Icon(Icons.Default.Remove, contentDescription = "sub", tint = PrimaryOrange)
                                }
                                Text(customQty.toString(), fontWeight = FontWeight.Bold, fontSize = 16.sp, modifier = Modifier.padding(horizontal = 12.dp))
                                IconButton(onClick = { customQty++ }) {
                                    Icon(Icons.Default.Add, contentDescription = "add", tint = PrimaryOrange)
                                }
                            }
                        }
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            val priceDouble = customPriceEstimate.toDoubleOrNull() ?: 150.0
                            if (customName.isNotBlank()) {
                                cartViewModel.addToCart(customName, priceDouble, customQty, true, "Custom Specific item Request")
                                showOtherItemDialog = false
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                        enabled = customName.isNotBlank()
                    ) {
                        Text("Add to Cart", color = OnPrimary, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showOtherItemDialog = false }) {
                        Text("Cancel", color = OnSurfaceVariant)
                    }
                }
            )
        }
    }
}

@Composable
fun MenuItemCard(
    item: MenuItem,
    onAddClick: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xAD1F1F1F)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onAddClick() }
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Box(modifier = Modifier.fillMaxWidth().aspectRatio(1.1f)) {
                AsyncImage(
                    model = getFoodImageUrl(item.name),
                    contentDescription = item.name,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )

                // Mock star rating tag matching design of gourmet kitfo / wat
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                        .background(BackgroundMidnight.copy(alpha = 0.6f), RoundedCornerShape(8.dp))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = "Rating star",
                            tint = AccentGold,
                            modifier = Modifier.size(10.dp)
                        )
                        Spacer(modifier = Modifier.width(3.dp))
                        Text(
                            text = "4.8",
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }
                }
            }

            Column(modifier = Modifier.padding(10.dp)) {
                Text(
                    text = item.name,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = OnSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Birr ${String.format("%.0f", item.price)}",
                        fontWeight = FontWeight.Bold,
                        color = SecondaryGold,
                        fontSize = 14.sp
                    )

                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .background(PrimaryContainerOrange, RoundedCornerShape(8.dp))
                            .clickable { onAddClick() },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "add item to cart",
                            tint = OnPrimary,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}
