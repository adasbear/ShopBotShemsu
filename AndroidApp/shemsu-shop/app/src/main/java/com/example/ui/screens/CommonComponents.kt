package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.ripple.rememberRipple
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*

fun getFoodImageUrl(name: String): String {
    val query = name.lowercase().trim()
    return when {
        query.contains("doro") || query.contains("wat") -> "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?q=80&w=600"
        query.contains("kitfo") -> "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=600"
        query.contains("fetira") || query.contains("pastry") || query.contains("bread") || query.contains("pancake") -> "https://images.unsplash.com/photo-1608897013039-887f21d8c804?q=80&w=600"
        query.contains("chechebsa") || query.contains("scramble") -> "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?q=80&w=600"
        query.contains("burger") -> "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=600"
        query.contains("pizza") -> "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=600"
        query.contains("pepsi") || query.contains("cola") || query.contains("soda") || query.contains("beverage") -> "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?q=80&w=600"
        query.contains("water") -> "https://images.unsplash.com/photo-1548964856-ac5755f70a5f?q=80&w=600"
        query.contains("coffee") || query.contains("espresso") || query.contains("brew") -> "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600"
        query.contains("juice") -> "https://images.unsplash.com/photo-1600271886742-f049cd451bba?q=80&w=600"
        query.contains("cake") || query.contains("sweet") || query.contains("dessert") -> "https://images.unsplash.com/photo-1578985545062-69928b1d9587?q=80&w=600"
        query.contains("salad") || query.contains("quinoa") || query.contains("harvest") -> "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=600"
        query.contains("tea") -> "https://images.unsplash.com/photo-1556679343-c7306c1976bc?q=80&w=600"
        query.contains("pasta") -> "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?q=80&w=600"
        else -> "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=600"
    }
}

@Composable
fun GlassCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    borderStroke: BorderStroke? = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
    content: @Composable ColumnScope.() -> Unit
) {
    val cardModifier = if (onClick != null) {
        modifier.clickable { onClick() }
    } else {
        modifier
    }

    Surface(
        modifier = cardModifier,
        shape = RoundedCornerShape(16.dp),
        color = Color(0x991E1E1E),
        tonalElevation = 4.dp,
        border = borderStroke
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            content = content
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ShemsuTopBar(
    title: String = "Shemsu Shop",
    showBack: Boolean = false,
    onBackClick: () -> Unit = {},
    showMenu: Boolean = true,
    onMenuClick: () -> Unit = {},
    onCartClick: () -> Unit = {},
    cartBadgeCount: Int = 0
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 22.sp,
                color = PrimaryOrange
            )
        },
        navigationIcon = {
            if (showBack) {
                IconButton(onClick = onBackClick) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = PrimaryOrange
                    )
                }
            } else if (showMenu) {
                IconButton(onClick = onMenuClick) {
                    Icon(
                        imageVector = Icons.Default.Menu,
                        contentDescription = "Menu Drawer",
                        tint = PrimaryOrange
                    )
                }
            }
        },
        actions = {
            IconButton(onClick = onCartClick) {
                BadgedBox(
                    badge = {
                        if (cartBadgeCount > 0) {
                            Badge(
                                containerColor = PrimaryContainerOrange,
                                contentColor = OnPrimary
                            ) {
                                Text(
                                    text = cartBadgeCount.toString(),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 10.sp
                                )
                            }
                        }
                    }
                ) {
                    Icon(
                        imageVector = Icons.Default.ShoppingCart,
                        contentDescription = "Shopping Cart",
                        tint = PrimaryOrange
                    )
                }
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = BackgroundMidnight.copy(alpha = 0.9f),
            titleContentColor = PrimaryOrange
        )
    )
}

@Composable
fun ShemsuBottomBar(
    currentRoute: String,
    onNavigate: (String) -> Unit,
    notificationsCount: Int = 0
) {
    NavigationBar(
        containerColor = SurfaceDeep.copy(alpha = 0.95f),
        tonalElevation = 8.dp,
        modifier = Modifier.windowInsetsPadding(WindowInsets.navigationBars)
    ) {
        val navItems = listOf(
            Triple("home", Icons.Default.Home, "Home"),
            Triple("menu", Icons.Default.RestaurantMenu, "Menu"),
            Triple("orders", Icons.Default.ReceiptLong, "Orders"),
            Triple("profile", Icons.Default.Person, "Profile")
        )

        navItems.forEach { (route, icon, label) ->
            val isSelected = currentRoute == route
            NavigationBarItem(
                selected = isSelected,
                onClick = { onNavigate(route) },
                icon = {
                    if (route == "profile" && notificationsCount > 0) {
                        BadgedBox(
                            badge = {
                                Badge(containerColor = StatusPending) {
                                    Text(notificationsCount.toString())
                                }
                            }
                        ) {
                            Icon(
                                imageVector = icon,
                                contentDescription = label,
                                tint = if (isSelected) OnPrimary else OnSurfaceVariant
                            )
                        }
                    } else {
                        Icon(
                            imageVector = icon,
                            contentDescription = label,
                            tint = if (isSelected) OnPrimary else OnSurfaceVariant
                        )
                    }
                },
                label = {
                    Text(
                        text = label,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                        color = if (isSelected) PrimaryOrange else OnSurfaceVariant.copy(alpha = 0.6f)
                    )
                },
                colors = NavigationBarItemDefaults.colors(
                    indicatorColor = PrimaryOrange,
                    selectedIconColor = OnPrimary,
                    unselectedIconColor = OnSurfaceVariant
                )
            )
        }
    }
}
