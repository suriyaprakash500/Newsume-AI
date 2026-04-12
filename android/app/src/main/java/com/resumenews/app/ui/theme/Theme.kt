package com.resumenews.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Blue700,
    onPrimary = White,
    primaryContainer = Blue200,
    secondary = Green600,
    surface = Gray50,
    background = White,
    onBackground = Gray900,
    onSurface = Gray900,
    outline = Gray300,
)

private val DarkColors = darkColorScheme(
    primary = Blue200,
    onPrimary = Gray900,
    primaryContainer = Blue700,
    secondary = Green600,
    surface = Gray900,
    background = Gray900,
    onBackground = White,
    onSurface = White,
    outline = Gray600,
)

@Composable
fun ResumeNewsTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkColors else LightColors
    MaterialTheme(
        colorScheme = colors,
        typography = AppTypography,
        content = content,
    )
}
