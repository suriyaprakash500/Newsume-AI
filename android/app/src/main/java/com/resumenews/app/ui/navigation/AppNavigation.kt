package com.resumenews.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Newspaper
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.lifecycle.viewmodel.compose.viewModel
import com.resumenews.app.ui.screens.DigestScreen
import com.resumenews.app.ui.screens.NewsScreen
import com.resumenews.app.ui.screens.ProfileScreen
import com.resumenews.app.ui.screens.ResumeScreen
import com.resumenews.app.viewmodel.NewsViewModel

sealed class Screen(val route: String, val label: String, val icon: ImageVector) {
    data object Resume : Screen("resume", "Resume", Icons.Filled.Description)
    data object News : Screen("news", "News", Icons.Filled.Newspaper)
    data object Digest : Screen("digest", "Digest", Icons.Filled.AutoAwesome)
    data object Profile : Screen("profile", "Profile", Icons.Filled.Person)
}

private val tabs = listOf(Screen.Resume, Screen.News, Screen.Digest, Screen.Profile)

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    Scaffold(
        bottomBar = {
            NavigationBar {
                tabs.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.label) },
                        label = { Text(screen.label) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        val newsViewModel: NewsViewModel = viewModel()

        NavHost(
            navController = navController,
            startDestination = Screen.Resume.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Resume.route) {
                ResumeScreen(
                    onProfileReady = {
                        navController.navigate(Screen.Profile.route) {
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable(Screen.News.route) {
                NewsScreen(viewModel = newsViewModel)
            }
            composable(Screen.Digest.route) {
                DigestScreen(viewModel = newsViewModel)
            }
            composable(Screen.Profile.route) {
                ProfileScreen()
            }
        }
    }
}
