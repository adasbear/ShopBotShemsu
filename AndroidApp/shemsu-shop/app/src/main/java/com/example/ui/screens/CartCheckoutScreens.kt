package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
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
import com.example.viewmodel.CartViewModel
import com.example.viewmodel.DebtViewModel
import com.example.viewmodel.OrdersViewModel
import com.example.ui.theme.*

@Composable
fun CartScreen(
    viewModel: CartViewModel,
    onNavigateCheckout: () -> Unit,
    onNavigateMenu: () -> Unit
) {
    val cartItems by viewModel.cartItems.collectAsState()
    val subtotal by viewModel.subtotal.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .padding(16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        // Title Header
        Text(
            text = "Your Cart",
            fontFamily = FontFamily.Serif,
            fontWeight = FontWeight.Bold,
            fontSize = 28.sp,
            color = OnSurface
        )
        Text(
            text = "${cartItems.sumOf { it.qty }} gourmet items added.",
            fontSize = 14.sp,
            color = OnSurfaceVariant.copy(alpha = 0.7f),
            modifier = Modifier.padding(top = 2.dp, bottom = 16.dp)
        )

        if (cartItems.isEmpty()) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                    modifier = Modifier.padding(24.dp).testTag("empty_cart_view")
                ) {
                    Box(
                        modifier = Modifier
                            .size(100.dp)
                            .background(Color(0xFF1E1E1E), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("🛒", fontSize = 42.sp)
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "Your Cart is Empty",
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp,
                        color = OnSurface
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        "Browse our wonderful menus of artisanal harvest dishes and select your premium choices.",
                        fontSize = 13.sp,
                        color = OnSurfaceVariant,
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = onNavigateMenu,
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Text("Explore Menu", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 14.sp)
                    }
                }
            }
        } else {
            Column(modifier = Modifier.weight(1f)) {
                LazyColumn(
                    modifier = Modifier.weight(1f).fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    contentPadding = PaddingValues(bottom = 16.dp)
                ) {
                    items(cartItems) { item ->
                        CartListItemRow(
                            item = item,
                            onQtyChange = { q -> viewModel.updateQty(item.name, q) },
                            onDelete = { viewModel.removeFromCart(item.name) }
                        )
                    }
                }

                // Divider and Totals
                Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.05f), modifier = Modifier.padding(vertical = 12.dp))

                GlassCard(modifier = Modifier.fillMaxWidth().padding(bottom = 80.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Subtotal", color = OnSurfaceVariant)
                        Text("Birr ${String.format("%.2f", subtotal)}", color = OnSurface, fontWeight = FontWeight.Bold)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Delivery/Service Fee", color = OnSurfaceVariant)
                        Text("Birr 80.00", color = OnSurface, fontWeight = FontWeight.Bold)
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.03f))
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("GRAND TOTAL", fontWeight = FontWeight.Bold, fontSize = 15.sp, color = OnSurface)
                        Text(
                            "Birr ${String.format("%.2f", subtotal + 80.0)}",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 22.sp,
                            color = SecondaryGold
                        )
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    Button(
                        onClick = onNavigateCheckout,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(54.dp)
                            .testTag("proceed_checkout_button"),
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                        shape = RoundedCornerShape(27.dp)
                    ) {
                        Text("Proceed to Checkout", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 16.sp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Icon(imageVector = Icons.Default.ArrowForward, contentDescription = "checkout direct", tint = OnPrimary)
                    }
                }
            }
        }
    }
}

@Composable
fun CartListItemRow(
    item: CartItem,
    onQtyChange: (Int) -> Unit,
    onDelete: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF161616)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.03f)),
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth().testTag("cart_item_${item.name}")
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(RoundedCornerShape(8.dp))
            ) {
                AsyncImage(
                    model = getFoodImageUrl(item.name),
                    contentDescription = item.name,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.name,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = OnSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                if (item.comment.isNotBlank()) {
                    Text(
                        text = item.comment,
                        fontSize = 11.sp,
                        color = PrimaryOrange.copy(alpha = 0.7f),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Birr ${String.format("%.2f", item.price)}",
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    color = SecondaryGold
                )
            }

            // Quantity modification and delete
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.End
            ) {
                IconButton(
                    onClick = { onQtyChange(item.qty - 1) },
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(Icons.Default.Remove, contentDescription = "sub qty", tint = OnSurfaceVariant, modifier = Modifier.size(16.dp))
                }
                Text(
                    text = item.qty.toString(),
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    color = OnSurface,
                    modifier = Modifier.width(24.dp),
                    textAlign = TextAlign.Center
                )
                IconButton(
                    onClick = { onQtyChange(item.qty + 1) },
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = "add qty", tint = OnSurfaceVariant, modifier = Modifier.size(16.dp))
                }

                Spacer(modifier = Modifier.width(8.dp))

                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "delete", tint = StatusError, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}

// --- CHECKOUT SCREEN ---
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun CheckoutScreen(
    ordersViewModel: OrdersViewModel,
    debtViewModel: DebtViewModel,
    cartViewModel: CartViewModel,
    onSuccessPlaced: (orderGroup: String) -> Unit,
    onBack: () -> Unit
) {
    val cartItems by cartViewModel.cartItems.collectAsState()
    val subtotal by cartViewModel.subtotal.collectAsState()
    val allowDebt by debtViewModel.allowDebt.collectAsState()
    val bankAccounts by debtViewModel.paymentAccounts.collectAsState()
    val isLoading by ordersViewModel.isLoading.collectAsState()

    var selectedMethod by remember { mutableStateOf("CBE Transfer") }
    var selectedBankId by remember { mutableStateOf(1) }
    var txConfirmationCode by remember { mutableStateOf("") }
    var userComment by remember { mutableStateOf("") }

    val scrollState = rememberScrollState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
                .padding(16.dp)
        ) {
            Spacer(modifier = Modifier.height(8.dp))

            // Header Back row
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = PrimaryOrange)
                }
                Text(
                    "Checkout Settlement",
                    fontFamily = FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface,
                    fontSize = 22.sp
                )
            }

            Text(
                "SELECT PAYMENT METHOD",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = OnSurfaceVariant,
                letterSpacing = 1.5.sp
            )

            Spacer(modifier = Modifier.height(10.dp))

            // Method cards: CBE Transfer, Telebirr, Debt
            Row(modifier = Modifier.fillMaxWidth()) {
                val methods = listOf(
                    Triple("CBE Transfer", Icons.Default.AccountBalance, "CBE"),
                    Triple("Telebirr", Icons.Default.Savings, "Telebirr"),
                    Triple("Debt", Icons.Default.AccountBalanceWallet, "Debt")
                )

                methods.forEach { (methodName, icon, abr) ->
                    val isChecked = selectedMethod == methodName
                    val isEnabled = methodName != "Debt" || allowDebt

                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (isChecked) Color(0xFF32231A) else Color(0xFF1E1E1E)
                        ),
                        border = BorderStroke(
                            1.dp,
                            if (isChecked) PrimaryOrange else Color(0x11FFFFFF)
                        ),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier
                            .weight(1f)
                            .padding(horizontal = 4.dp)
                            .clickable(enabled = isEnabled) {
                                selectedMethod = methodName
                            }
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Icon(
                                imageVector = icon,
                                contentDescription = methodName,
                                tint = if (isChecked) PrimaryOrange else if (isEnabled) OnSurfaceVariant else OnSurfaceVariant.copy(alpha = 0.2f),
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                abr,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp,
                                color = if (isChecked) OnSurface else if (isEnabled) OnSurfaceVariant else OnSurfaceVariant.copy(alpha = 0.2f)
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Selected Payment Method Detail Blocks
            AnimatedContent(targetState = selectedMethod, label = "method_detail") { method ->
                when (method) {
                    "CBE Transfer" -> {
                        CbeInstructionsTile(accounts = bankAccounts, onSelectId = { selectedBankId = it }, activeId = selectedBankId)
                    }
                    "Telebirr" -> {
                        TelebirrInstructionsTile(accounts = bankAccounts)
                    }
                    "Debt" -> {
                        DebtCheckTile(allow = allowDebt)
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Transaction confirmation text field (Required if CBE or Telebirr)
            if (selectedMethod != "Debt") {
                Text(
                    text = "TRANSACTION CONFIRMATION REF#",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurfaceVariant
                )
                Spacer(modifier = Modifier.height(6.dp))
                OutlinedTextField(
                    value = txConfirmationCode,
                    onValueChange = { txConfirmationCode = it },
                    placeholder = { Text("Transfer transaction ID (e.g. CBE2362A...)", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth().testTag("ref_input"),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = PrimaryOrange,
                        unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f)
                    )
                )

                Spacer(modifier = Modifier.height(16.dp))
            }

            // Optional note
            Text(
                text = "SPECIAL INSTRUCTIONS / REMARKS",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = OnSurfaceVariant
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = userComment,
                onValueChange = { userComment = it },
                placeholder = { Text("Eg. deliver around 12:00 PM / please don't add salt / ring doorbell", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                modifier = Modifier.fillMaxWidth(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = PrimaryOrange,
                    unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f)
                )
            )

            Spacer(modifier = Modifier.height(28.dp))

            // Checkout Summary block and Button
            GlassCard(modifier = Modifier.fillMaxWidth().padding(bottom = 80.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Total Items", color = OnSurfaceVariant)
                    Text("${cartItems.sumOf { it.qty }} dishes", color = OnSurface, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Settlement Method", color = OnSurfaceVariant)
                    Text(selectedMethod, color = PrimaryOrange, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.height(12.dp))
                Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.03f))
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("SETTLEMENT TOTAL", fontWeight = FontWeight.Bold, fontSize = 14.sp, color = OnSurface)
                    Text(
                        "Birr ${String.format("%.2f", subtotal + 80.0)}",
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 24.sp,
                        color = SecondaryGold
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                val isButtonEnabled = selectedMethod == "Debt" || txConfirmationCode.trim().isNotEmpty()

                Button(
                    onClick = {
                        ordersViewModel.placeOrder(
                            items = cartItems,
                            paymentMethod = selectedMethod,
                            paymentAccountId = if (selectedMethod == "CBE Transfer") selectedBankId else null,
                            confirmation = if (selectedMethod != "Debt") txConfirmationCode else null,
                            comment = userComment,
                            onSuccess = { gId ->
                                cartViewModel.clearCart()
                                onSuccessPlaced(gId)
                            }
                        )
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                        .testTag("place_order_button"),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                    shape = RoundedCornerShape(28.dp),
                    enabled = !isLoading && isButtonEnabled
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(color = OnPrimary, modifier = Modifier.size(24.dp))
                    } else {
                        Text("Place Gourmet Order", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 16.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun CbeInstructionsTile(
    accounts: List<com.example.data.model.PaymentAccount>,
    onSelectId: (Int) -> Unit,
    activeId: Int
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF161616)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.03f)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Commercial Bank of Ethiopia (CBE)",
                fontWeight = FontWeight.Bold,
                fontSize = 15.sp,
                color = OnSurface
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                "Please wire the settlement total to our account and input the reference code below. Choose an account below:",
                fontSize = 12.sp,
                color = OnSurfaceVariant
            )

            Spacer(modifier = Modifier.height(12.dp))

            accounts.filter { it.bank_name.contains("CBE", ignoreCase = true) }.forEach { acc ->
                val selected = activeId == acc.id
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .background(
                            if (selected) Color(0x19FFB68A) else Color.Transparent,
                            RoundedCornerShape(8.dp)
                        )
                        .border(
                            1.dp,
                            if (selected) PrimaryOrange.copy(alpha = 0.3f) else Color.Transparent,
                            RoundedCornerShape(8.dp)
                        )
                        .clickable { onSelectId(acc.id) }
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(acc.holder_name, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = OnSurface)
                        Text(acc.number, fontFamily = FontFamily.Monospace, fontSize = 14.sp, color = SecondaryGold)
                    }
                    if (selected) {
                        Icon(Icons.Default.Check, contentDescription = "selected", tint = PrimaryOrange, modifier = Modifier.size(18.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun TelebirrInstructionsTile(
    accounts: List<com.example.data.model.PaymentAccount>
) {
    val tele = accounts.firstOrNull { it.bank_name.contains("Telebirr", ignoreCase = true) }
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF161616)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.03f)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Telebirr Settlement",
                fontWeight = FontWeight.Bold,
                fontSize = 15.sp,
                color = OnSurface
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                "Transfer via Telebirr merchant pay or mobile number, then specify transaction code.",
                fontSize = 12.sp,
                color = OnSurfaceVariant
            )
            if (tele != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.03f))
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "Telebirr Recipient: ${tele.holder_name}",
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 13.sp,
                    color = OnSurface
                )
                Text(
                    text = "Merchant No / Phone: ${tele.number}",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = PrimaryOrange,
                    fontFamily = FontFamily.Monospace
                )
            }
        }
    }
}

@Composable
fun DebtCheckTile(allow: Boolean) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF161616)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.03f)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (allow) Icons.Default.Info else Icons.Default.Warning,
                    contentDescription = "status",
                    tint = if (allow) SecondaryGold else StatusError,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = if (allow) "Debt Settlement Checked" else "Settlement Denied",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = if (allow) OnSurface else StatusError
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = if (allow) {
                    "Your debt allowance is healthy. This order will be recorded in our system as a balance due. Access limits are reviewed weekly."
                } else {
                    "Your active debt limit has been exceeded. Please settle past debts in the Debt Center before placing a new debt order."
                },
                fontSize = 12.sp,
                color = OnSurfaceVariant
            )
        }
    }
}

// --- ORDER SUCCESS SCREEN ---
@Composable
fun OrderSuccessScreen(
    orderGroup: String,
    onNavigateOrders: () -> Unit,
    onNavigateDashboard: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(110.dp)
                    .background(Color(0x114CAF50), CircleShape)
                    .border(2.dp, StatusAccepted, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Success check",
                    tint = StatusAccepted,
                    modifier = Modifier.size(48.dp)
                )
            }

            Spacer(modifier = Modifier.height(28.dp))

            Text(
                text = "Order Placed Successfully! 🎉",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 24.sp,
                color = OnSurface,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "The kitchens of Al-Shemsu have received your order details and preparation has commenced.",
                fontSize = 13.sp,
                color = OnSurfaceVariant,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Order key box
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
                modifier = Modifier.width(260.dp).testTag("success_order_id_box")
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("ORDER REFERENCE", fontSize = 10.sp, color = OnSurfaceVariant)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = orderGroup,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp,
                        color = SecondaryGold
                    )
                }
            }

            Spacer(modifier = Modifier.height(40.dp))

            Button(
                onClick = onNavigateOrders,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("track_order_button"),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                shape = RoundedCornerShape(25.dp)
            ) {
                Text("Track My Order", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 15.sp)
            }

            Spacer(modifier = Modifier.height(12.dp))

            OutlinedButton(
                onClick = onNavigateDashboard,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.1f)),
                shape = RoundedCornerShape(25.dp)
            ) {
                Text("Return to Dashboard", fontWeight = FontWeight.Bold, color = OnSurface, fontSize = 15.sp)
            }
        }
    }
}
