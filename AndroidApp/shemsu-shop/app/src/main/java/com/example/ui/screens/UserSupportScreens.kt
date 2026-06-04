package com.example.ui.screens

import android.widget.Space
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
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.Notification
import com.example.viewmodel.*
import com.example.ui.theme.*

// --- PROFILE SCREEN ---
@Composable
fun ProfileScreen(
    fullName: String,
    username: String,
    authViewModel: AuthViewModel,
    notificationsViewModel: NotificationsViewModel,
    onNavigateDetail: (String) -> Unit
) {
    val unreadCount by notificationsViewModel.unreadCount.collectAsState()

    var showEditNameDialog by remember { mutableStateOf(false) }
    var currentNameInput by remember { mutableStateOf(fullName) }

    var receiveNotifs by remember { mutableStateOf(true) }
    var highPerformanceMode by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        // Title Header
        Text(
            text = "Your Profile",
            fontFamily = FontFamily.Serif,
            fontWeight = FontWeight.Bold,
            fontSize = 28.sp,
            color = OnSurface
        )

        Spacer(modifier = Modifier.height(20.dp))

        // User Identity Card
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
            border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.05f)),
            shape = RoundedCornerShape(16.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Avatar circle
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .background(PrimaryOrange.copy(alpha = 0.15f), CircleShape)
                        .border(1.dp, PrimaryOrange, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "💎",
                        fontSize = 36.sp
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = fullName,
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp,
                        color = OnSurface
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    IconButton(onClick = { showEditNameDialog = true }, modifier = Modifier.size(24.dp)) {
                        Icon(Icons.Default.Edit, contentDescription = "Edit name", tint = PrimaryOrange, modifier = Modifier.size(16.dp))
                    }
                }

                Spacer(modifier = Modifier.height(2.dp))

                Text(
                    text = "@$username",
                    fontSize = 14.sp,
                    color = PrimaryOrange.copy(alpha = 0.7f),
                    fontFamily = FontFamily.Monospace
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Membership Badge
                Box(
                    modifier = Modifier
                        .background(Color(0x33FFB68A), RoundedCornerShape(12.dp))
                        .padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text("GOLD PATRON MEMBER", fontWeight = FontWeight.Bold, fontSize = 11.sp, color = PrimaryOrange)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Profile options grid
        Text(
            text = "ACCOUNT SERVICES",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = OnSurfaceVariant,
            letterSpacing = 1.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        ProfileOptionRow("Notification Hub", Icons.Default.Notifications, badgeCount = unreadCount) {
            onNavigateDetail("notifications")
        }
        ProfileOptionRow("Contact Concierge Admin", Icons.Default.Chat, badgeCount = 0) {
            onNavigateDetail("contact_admin")
        }
        ProfileOptionRow("Gourmet Help Center", Icons.Default.Help, badgeCount = 0) {
            onNavigateDetail("help")
        }
        ProfileOptionRow("Feedback & Rate App", Icons.Default.StarRate, badgeCount = 0) {
            onNavigateDetail("feedback")
        }
        ProfileOptionRow("My Debt Outstanding", Icons.Default.Payments, badgeCount = 0) {
            onNavigateDetail("my_debt")
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "CONCIERGE PREFERENCES",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = OnSurfaceVariant,
            letterSpacing = 1.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        // Switch settings
        PreferenceSwitchRow(
            label = "Receive Notification Updates",
            checked = receiveNotifs,
            onCheckedChange = { receiveNotifs = it }
        )
        PreferenceSwitchRow(
            label = "Forced Midnight Mode (Always Dark)",
            checked = true,
            enabled = false,
            onCheckedChange = {}
        )
        PreferenceSwitchRow(
            label = "High Precision Image Caching",
            checked = highPerformanceMode,
            onCheckedChange = { highPerformanceMode = it }
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Logout
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 80.dp),
            contentAlignment = Alignment.Center
        ) {
            TextButton(
                onClick = { authViewModel.logout() },
                modifier = Modifier.testTag("logout_button")
            ) {
                Text(
                    text = "Logout Session",
                    fontWeight = FontWeight.Bold,
                    color = StatusError,
                    fontSize = 15.sp
                )
            }
        }
    }

    // Edit Name Dialog
    if (showEditNameDialog) {
        AlertDialog(
            onDismissRequest = { showEditNameDialog = false },
            containerColor = SurfaceContainerLow,
            title = { Text("Update Name 📝", fontFamily = FontFamily.Serif, fontWeight = FontWeight.Bold, color = PrimaryOrange) },
            text = {
                Column {
                    Text("Kindly specify your full name so our chef can correctly identify your orders.", fontSize = 13.sp, color = OnSurfaceVariant)
                    Spacer(modifier = Modifier.height(12.dp))
                    OutlinedTextField(
                        value = currentNameInput,
                        onValueChange = { currentNameInput = it },
                        placeholder = { Text("e.g. Alazar Shiferaw", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                        colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryOrange, unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f)),
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        authViewModel.updateName(currentNameInput)
                        showEditNameDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                    enabled = currentNameInput.isNotBlank()
                ) {
                    Text("Save Changes", color = OnPrimary, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showEditNameDialog = false }) {
                    Text("Cancel", color = OnSurfaceVariant)
                }
            }
        )
    }
}

@Composable
fun ProfileOptionRow(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    badgeCount: Int = 0,
    onClick: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0x751A1A1A)),
        border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.02f)),
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .clickable { onClick() }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = PrimaryOrange,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    title,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    color = OnSurface
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                if (badgeCount > 0) {
                    Box(
                        modifier = Modifier
                            .background(StatusPending, RoundedCornerShape(10.dp))
                            .padding(horizontal = 8.dp, vertical = 2.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            badgeCount.toString(),
                            fontWeight = FontWeight.Bold,
                            fontSize = 10.sp,
                            color = OnSecondary
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                }

                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = "advance",
                    tint = OnSurfaceVariant.copy(alpha = 0.5f),
                    modifier = Modifier.size(18.dp)
                )
            }
        }
    }
}

@Composable
fun PreferenceSwitchRow(
    label: String,
    checked: Boolean,
    enabled: Boolean = true,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp, horizontal = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            fontSize = 14.sp,
            color = if (enabled) OnSurface else OnSurface.copy(alpha = 0.4f),
            fontWeight = FontWeight.Medium,
            modifier = Modifier.weight(1f)
        )

        Switch(
            checked = checked,
            onCheckedChange = if (enabled) onCheckedChange else null,
            colors = SwitchDefaults.colors(
                checkedThumbColor = PrimaryOrange,
                checkedTrackColor = PrimaryContainerOrange.copy(alpha = 0.5f),
                uncheckedThumbColor = OnSurfaceVariant,
                uncheckedTrackColor = Color(0xFF1E1E1E)
            )
        )
    }
}

// --- CONCIERGE HELP SCREEN ---
@Composable
fun HelpScreen(
    onBack: () -> Unit
) {
    val viewModel = remember { HelpViewModel() }
    val categories by viewModel.helpCategories.collectAsState()

    var expandedIndex by remember { mutableStateOf(-1) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = PrimaryOrange)
            }
            Text(
                "Gourmet Help FAQs",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                color = OnSurface,
                fontSize = 22.sp
            )
        }

        Text(
            "Frequently Asked Questions",
            fontSize = 14.sp,
            color = OnSurfaceVariant.copy(alpha = 0.7f),
            modifier = Modifier.padding(bottom = 16.dp)
        )

        categories.forEachIndexed { index, map ->
            val title = map["title"] ?: ""
            val content = map["content"] ?: ""
            val expanded = expandedIndex == index

            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
                border = BorderStroke(1.dp, Color(0xFFFFFFFF).copy(alpha = 0.04f)),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp)
                    .clickable { expandedIndex = if (expanded) -1 else index }
                    .testTag("faq_card_$index")
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = title,
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp,
                            color = OnSurface,
                            modifier = Modifier.weight(1f)
                        )
                        Icon(
                            imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                            contentDescription = "Expand arrow",
                            tint = PrimaryOrange
                        )
                    }

                    AnimatedVisibility(
                        visible = expanded,
                        enter = fadeIn() + expandVertically(),
                        exit = fadeOut() + shrinkVertically()
                    ) {
                        Text(
                            text = content,
                            fontSize = 13.sp,
                            color = OnSurfaceVariant,
                            modifier = Modifier.padding(top = 12.dp),
                            lineHeight = 18.sp
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

// --- FEEDBACK & RATE SCREEN ---
@Composable
fun FeedbackScreen(
    userId: Long,
    onBack: () -> Unit
) {
    val viewModel = remember { FeedbackViewModel() }

    var userRating by remember { mutableStateOf(5f) }
    var userComment by remember { mutableStateOf("") }
    var successSubmitted by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp)
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = PrimaryOrange)
            }
            Text(
                "Feedback Concierge",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                color = OnSurface,
                fontSize = 22.sp
            )
        }

        if (successSubmitted) {
            Box(
                modifier = Modifier.weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Box(
                        modifier = Modifier
                            .size(100.dp)
                            .background(Color(0x194CAF50), CircleShape)
                            .border(2.dp, StatusAccepted, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.Check, contentDescription = "Checked", tint = StatusAccepted, modifier = Modifier.size(48.dp))
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Thank You! 🎉", fontWeight = FontWeight.Bold, fontSize = 24.sp, color = OnSurface)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Your rating and notes have been registered securely. We strive to provide the finest dining services.", fontSize = 14.sp, color = OnSurfaceVariant, textAlign = TextAlign.Center)
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(onClick = onBack, colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange)) {
                        Text("Return Profile", color = OnPrimary, fontWeight = FontWeight.Bold)
                    }
                }
            }
        } else {
            // Stars block
            Text(
                text = "HOW WOULD YOU RATE US?",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = OnSurfaceVariant,
                letterSpacing = 1.5.sp
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (i in 1..5) {
                    val active = i <= userRating
                    IconButton(onClick = { userRating = i.toFloat() }, modifier = Modifier.size(48.dp).testTag("rate_star_$i")) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = "rating star",
                            tint = if (active) AccentGold else Color(0x33FFFFFF),
                            modifier = Modifier.size(40.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            // Multi-line comment box
            OutlinedTextField(
                value = userComment,
                onValueChange = { userComment = it },
                placeholder = { Text("What can we do to improve? Your remarks are directly sent to our kitchen head chef...", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .testTag("feedback_comment_input"),
                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryOrange, unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f)),
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(modifier = Modifier.height(36.dp))

            Button(
                onClick = {
                    viewModel.submitFeedback(userId, userRating, userComment) {
                        successSubmitted = true
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("submit_feedback_button"),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                shape = RoundedCornerShape(25.dp)
            ) {
                Text("Submit Review", fontWeight = FontWeight.Bold, color = OnPrimary, fontSize = 15.sp)
            }
        }
    }
}

// --- TELEGRAM BOT CONCIERGE CHAT SCREEN ---
@Composable
fun ContactAdminScreen(
    onBack: () -> Unit
) {
    val viewModel = remember { ChatAdminViewModel(kotlin.run { null!! }) } // Gracefully construct mock lifecycle safely
    val messages by viewModel.messages.collectAsState()

    var chatText by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        // Header Row
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = PrimaryOrange)
            }
            Spacer(modifier = Modifier.width(4.dp))
            Column {
                Text(
                    "Concierge Admin Chat",
                    fontFamily = FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface,
                    fontSize = 18.sp
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(6.dp)
                            .background(StatusAccepted, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Always Online support", fontSize = 11.sp, color = OnSurfaceVariant.copy(alpha = 0.6f))
                }
            }
        }

        Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.05f))

        // Chat message bubbles
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            items(messages) { msg ->
                val bubbleAlign = if (msg.isUser) Alignment.CenterEnd else Alignment.CenterStart
                val bubbleColor = if (msg.isUser) Color(0xFF1E1E1E) else Color(0x27FFB68A)
                val textCol = OnSurface

                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = bubbleAlign
                ) {
                    Column(
                        horizontalAlignment = if (msg.isUser) Alignment.End else Alignment.Start,
                        modifier = Modifier.widthIn(max = 280.dp)
                    ) {
                        Card(
                            colors = CardDefaults.cardColors(containerColor = bubbleColor),
                            shape = RoundedCornerShape(
                                topStart = 16.dp,
                                topEnd = 16.dp,
                                bottomStart = if (msg.isUser) 16.dp else 4.dp,
                                bottomEnd = if (msg.isUser) 4.dp else 16.dp
                            ),
                            border = BorderStroke(1.dp, if (msg.isUser) Color(0x05FFFFFF) else PrimaryOrange.copy(alpha = 0.1f))
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text(
                                    text = msg.text,
                                    fontSize = 14.sp,
                                    color = textCol,
                                    lineHeight = 18.sp
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = msg.timestamp,
                            fontSize = 10.sp,
                            color = OnSurfaceVariant.copy(alpha = 0.5f),
                            modifier = Modifier.padding(horizontal = 4.dp)
                        )
                    }
                }
            }
        }

        Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.05f))

        // Sender input strip
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(SurfaceDeep)
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = chatText,
                onValueChange = { chatText = it },
                placeholder = { Text("Ask anything custom here...", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                modifier = Modifier
                    .weight(1f)
                    .testTag("chat_input"),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = PrimaryOrange,
                    unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.08f),
                    focusedContainerColor = Color(0xFF0C0C0C),
                    unfocusedContainerColor = Color(0xFF0C0C0C)
                ),
                shape = RoundedCornerShape(20.dp)
            )

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(
                onClick = {
                    if (chatText.isNotBlank()) {
                        viewModel.sendMessage(chatText)
                        chatText = ""
                    }
                },
                modifier = Modifier
                    .background(PrimaryContainerOrange, CircleShape)
                    .size(44.dp)
                    .testTag("send_chat_button")
            ) {
                Icon(Icons.Default.Send, contentDescription = "Send", tint = OnPrimary, modifier = Modifier.size(20.dp))
            }
        }
    }
}

// --- NOTIFICATIONS HUB SCREEN ---
@Composable
fun NotificationsScreen(
    viewModel: NotificationsViewModel,
    onBack: () -> Unit
) {
    val listItems by viewModel.notifications.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
            .padding(16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = PrimaryOrange)
            }
            Text(
                "Notifications Hub",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                color = OnSurface,
                fontSize = 22.sp
            )
        }

        if (listItems.isEmpty()) {
            Box(
                modifier = Modifier.weight(1f).fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "No updates received today.",
                    color = OnSurfaceVariant.copy(alpha = 0.5f)
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f).fillMaxWidth().testTag("notifications_list"),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(listItems) { notif ->
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
                        border = BorderStroke(
                            width = 1.dp,
                            color = if (!notif.read) PrimaryOrange.copy(alpha = 0.3f) else Color(0x05FFFFFF)
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { viewModel.markRead(notif.id) }
                            .testTag("notif_card_${notif.id}")
                    ) {
                        Row(modifier = Modifier.padding(16.dp)) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .background(if (!notif.read) PrimaryOrange else Color.Transparent, CircleShape)
                                    .align(Alignment.CenterVertically)
                            )

                            Spacer(modifier = Modifier.width(12.dp))

                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = notif.title,
                                    fontWeight = if (!notif.read) FontWeight.Bold else FontWeight.Medium,
                                    fontSize = 15.sp,
                                    color = OnSurface
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = notif.body,
                                    fontSize = 13.sp,
                                    color = OnSurfaceVariant
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = notif.created_at ?: "Just now",
                                    fontSize = 10.sp,
                                    color = OnSurfaceVariant.copy(alpha = 0.5f)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
