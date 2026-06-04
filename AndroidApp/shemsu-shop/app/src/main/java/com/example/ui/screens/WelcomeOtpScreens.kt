package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.content.Intent
import android.net.Uri
import androidx.compose.ui.platform.LocalContext
import coil.compose.AsyncImage
import com.example.viewmodel.AuthViewModel
import com.example.ui.theme.*
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(
    viewModel: AuthViewModel,
    onNavigateNext: (isLoggedIn: Boolean) -> Unit
) {
    LaunchedEffect(Unit) {
        delay(1200)
        viewModel.validateSessionSilently { isValid ->
            onNavigateNext(isValid)
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight),
        contentAlignment = Alignment.Center
    ) {
        // Subtle background decoration blur
        Box(
            modifier = Modifier
                .size(300.dp)
                .blur(80.dp)
                .background(
                    Brush.radialGradient(
                        listOf(PrimaryContainerOrange.copy(alpha = 0.15f), Color.Transparent)
                    )
                )
        )

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(24.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .border(1.dp, PrimaryOrange.copy(alpha = 0.3f), CircleShape)
                    .background(Color(0xFF1E1E1E), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "🍽️",
                    fontSize = 42.sp
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "Shemsu Shop",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 32.sp,
                color = PrimaryOrange,
                letterSpacing = (-0.5).sp
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "THE MIDNIGHT HARVEST",
                fontWeight = FontWeight.Medium,
                fontSize = 11.sp,
                color = OnSurfaceVariant.copy(alpha = 0.6f),
                letterSpacing = 2.sp
            )

            Spacer(modifier = Modifier.height(48.dp))

            CircularProgressIndicator(
                color = PrimaryContainerOrange,
                strokeWidth = 3.dp,
                modifier = Modifier.size(36.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Preparing your gourmet experience...",
                fontSize = 12.sp,
                color = OnSurfaceVariant.copy(alpha = 0.4f)
            )
        }
    }
}

@Composable
fun LoginScreen(
    viewModel: AuthViewModel,
    onLoginSuccess: () -> Unit
) {
    val isLoggedIn by viewModel.isLoggedIn.collectAsState()
    val username by viewModel.username.collectAsState()
    val otpSent by viewModel.otpSent.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val authError by viewModel.authError.collectAsState()

    var usernameInput by remember { mutableStateOf("") }
    var otpCode by remember { mutableStateOf("") }

    val focusManager = LocalFocusManager.current

    LaunchedEffect(isLoggedIn) {
        if (isLoggedIn) {
            onLoginSuccess()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundMidnight)
    ) {
        // Atmospheric gradient glow background
        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(250.dp)
                .blur(100.dp)
                .background(Brush.radialGradient(listOf(PrimaryOrange.copy(alpha = 0.1f), Color.Transparent)))
        )
        Box(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .size(250.dp)
                .blur(100.dp)
                .background(Brush.radialGradient(listOf(SecondaryGold.copy(alpha = 0.08f), Color.Transparent)))
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // App name header (Identity only)
            Text(
                text = "Shemsu Shop",
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Bold,
                fontSize = 24.sp,
                color = PrimaryOrange,
                modifier = Modifier.padding(bottom = 32.dp)
            )

            // Featured Salad decoration
            Box(
                modifier = Modifier
                    .size(160.dp)
                    .border(2.dp, PrimaryOrange.copy(alpha = 0.2f), CircleShape)
                    .padding(4.dp),
                contentAlignment = Alignment.Center
            ) {
                AsyncImage(
                    model = "https://lh3.googleusercontent.com/aida-public/AB6AXuDDSjqMPkhRCYlcZjuO_eGa0VSj4q0aQarTVVvymvCaUtqA4DaJMwC2o-cCVtwHyq60W2Cfiklk06ffruFQseSWhu6ueZ0nLPFL4mGn2JmRmujCFsu4r4IDv7KKkXD1LyghhHafb6eKY6hQECG_sAGFMv78uVvS0IdADj4ekR4dW-n6ZwlPJoMwmAu9pwbn4QFObMdN3UQM5AEzKUCndPygtKN3pgrgxu0eE5IC_6lU8XmkmgJk8eNXYq3qrUzjokMHRiaA6ON43GA",
                    contentDescription = "Artisanal food banner",
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(CircleShape),
                    contentScale = ContentScale.Crop
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Login glass card
            GlassCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Welcome Back",
                    fontFamily = FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    fontSize = 28.sp,
                    color = OnSurface,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "Please register on @sshopdelivery_bot first. Then input your Telegram username below to get your security OTP code.",
                    fontSize = 14.sp,
                    color = OnSurfaceVariant,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Telegram username input
                Text(
                    text = "Telegram Username",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurfaceVariant.copy(alpha = 0.8f)
                )

                Spacer(modifier = Modifier.height(6.dp))

                OutlinedTextField(
                    value = usernameInput,
                    onValueChange = {
                        if (!otpSent) usernameInput = it
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("username_input"),
                    placeholder = { Text("username", color = OnSurfaceVariant.copy(alpha = 0.4f)) },
                    leadingIcon = {
                        Text(
                            text = "@",
                            fontWeight = FontWeight.Bold,
                            color = PrimaryOrange,
                            modifier = Modifier.padding(start = 12.dp, end = 4.dp)
                        )
                    },
                    singleLine = true,
                    enabled = !otpSent && !isLoading,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = PrimaryOrange,
                        unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f),
                        disabledBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.05f),
                        focusedContainerColor = Color(0xFF0F0F0F),
                        unfocusedContainerColor = Color(0xFF0F0F0F)
                    ),
                    shape = RoundedCornerShape(12.dp)
                )

                // OTP Verification layout
                AnimatedVisibility(
                    visible = otpSent,
                    enter = fadeIn() + expandVertically(),
                    exit = fadeOut() + shrinkVertically()
                ) {
                    Column(modifier = Modifier.padding(top = 16.dp)) {
                        Text(
                            text = "Verification Code",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurfaceVariant.copy(alpha = 0.8f)
                        )

                        Spacer(modifier = Modifier.height(6.dp))

                        OutlinedTextField(
                            value = otpCode,
                            onValueChange = {
                                if (it.length <= 6) {
                                    otpCode = it
                                    if (it.length == 6) {
                                        focusManager.clearFocus()
                                    }
                                }
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("otp_input"),
                            placeholder = { Text("6-digit code", color = OnSurfaceVariant.copy(alpha = 0.3f)) },
                            singleLine = true,
                            enabled = !isLoading,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = PrimaryOrange,
                                unfocusedBorderColor = Color(0xFFFFFFFF).copy(alpha = 0.1f),
                                focusedContainerColor = Color(0xFF0F0F0F),
                                unfocusedContainerColor = Color(0xFF0F0F0F)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        )
                        
                        Spacer(modifier = Modifier.height(4.dp))
                        
                        Text(
                            text = "Please check your Telegram DMs for the code.",
                            fontSize = 11.sp,
                            color = PrimaryOrange.copy(alpha = 0.7f),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }

                // Error statement
                if (authError != null) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = authError ?: "",
                        color = StatusError,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth()
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Primary Button
                if (!otpSent) {
                    Button(
                        onClick = {
                            focusManager.clearFocus()
                            viewModel.requestOtp(usernameInput)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp)
                            .testTag("send_otp_button"),
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryContainerOrange),
                        shape = RoundedCornerShape(28.dp),
                        enabled = !isLoading && usernameInput.isNotBlank()
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(color = OnPrimary, modifier = Modifier.size(24.dp))
                        } else {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "Send OTP",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp,
                                    color = OnPrimary
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Icon(
                                    imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                                    contentDescription = "Continue",
                                    tint = OnPrimary
                                )
                            }
                        }
                    }
                } else {
                    Button(
                        onClick = {
                            focusManager.clearFocus()
                            viewModel.verifyOtp(otpCode)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp)
                            .testTag("verify_otp_button"),
                        colors = ButtonDefaults.buttonColors(containerColor = StatusAccepted),
                        shape = RoundedCornerShape(28.dp),
                        enabled = !isLoading && otpCode.length == 6
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                        } else {
                            Text(
                                text = "Verify & Continue",
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                color = Color.White
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Divider(color = Color(0xFFFFFFFF).copy(alpha = 0.05f))

                Spacer(modifier = Modifier.height(16.dp))

                val context = LocalContext.current
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.clickable {
                            try {
                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://t.me/sshopdelivery_bot"))
                                context.startActivity(intent)
                            } catch (e: Exception) {
                                // Fallback
                            }
                        }
                    ) {
                        Icon(
                            imageVector = Icons.Default.SmartToy,
                            contentDescription = "Telegram bot",
                            tint = OnSurfaceVariant,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Open Telegram Bot",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant
                        )
                    }

                    Text(
                        text = "Need Help?",
                        fontSize = 12.sp,
                        color = AccentGold,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.clickable {
                            // Contact helpline mock
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            Text(
                text = "ARTISANAL QUALITY • SECURE ACCESS",
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium,
                color = OnSurfaceVariant.copy(alpha = 0.4f),
                letterSpacing = 1.5.sp
            )
        }
    }
}
