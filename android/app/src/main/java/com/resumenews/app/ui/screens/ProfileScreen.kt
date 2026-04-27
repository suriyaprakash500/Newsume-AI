package com.resumenews.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.InputChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.gson.Gson
import com.resumenews.app.viewmodel.ResumeViewModel

@Composable
fun ProfileScreen(viewModel: ResumeViewModel = viewModel()) {
    val profile by viewModel.profile.collectAsState()
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.fetchPreferences()
    }

    LaunchedEffect(uiState.saveSuccess) {
        if (uiState.saveSuccess) {
            snackbarHostState.showSnackbar("Profile saved!")
            viewModel.clearSaveSuccess()
        }
    }
    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearError()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        if (profile == null) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "No profile yet. Upload your resume first!",
                    style = MaterialTheme.typography.bodyLarge
                )
            }
            return@Scaffold
        }

        val p = profile!!
        val gson = Gson()

        val editableSkills = remember(p.skills) { mutableStateListOf(*parseList(gson, p.skills).toTypedArray()) }
        val editableCerts = remember(p.certifications) { mutableStateListOf(*parseList(gson, p.certifications).toTypedArray()) }
        val editableKeywords = remember(p.keywords) { mutableStateListOf(*parseList(gson, p.keywords).toTypedArray()) }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Text(
                text = p.name.ifBlank { "Your Profile" },
                style = MaterialTheme.typography.headlineMedium,
            )
            Text(
                text = "Resume v${p.version} — ${p.resumeFilename}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Tap any section to edit, then Save",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Spacer(modifier = Modifier.height(24.dp))

            EditableProfileSection("Skills", editableSkills)
            EditableProfileSection("Certifications", editableCerts)
            ProfileSection("Experience", parseList(gson, p.experience))
            ProfileSection("Education", parseList(gson, p.education))
            EditableProfileSection("Keywords", editableKeywords)

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    viewModel.saveProfileEdits(
                        skills = editableSkills.toList(),
                        certifications = editableCerts.toList(),
                        keywords = editableKeywords.toList(),
                    )
                },
                enabled = !uiState.isSaving,
                modifier = Modifier.fillMaxWidth(),
            ) {
                if (uiState.isSaving) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                } else {
                    Icon(Icons.Filled.Save, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                }
                Text("Save Profile")
            }

            Spacer(modifier = Modifier.height(32.dp))
            
            uiState.preferences?.let { prefs ->
                PreferencesSection(
                    prefs = prefs,
                    isSaving = uiState.isSavingPrefs,
                    onSave = { pTopics, bTopics, seniority, notify, start, end ->
                        viewModel.savePreferences(pTopics, bTopics, seniority, notify, start, end)
                    }
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            SkillGapSection(
                report = uiState.skillGapReport,
                isLoading = uiState.isLoadingSkillGap,
                onFetch = { viewModel.fetchSkillGapReport() }
            )

            Spacer(modifier = Modifier.height(16.dp))

            val context = androidx.compose.ui.platform.LocalContext.current
            Button(
                onClick = { viewModel.deleteProfile(context) },
                enabled = !uiState.isDeleting,
                modifier = Modifier.fillMaxWidth(),
                colors = androidx.compose.material3.ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                if (uiState.isDeleting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onError,
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                }
                Text("Delete Profile & Reset Data")
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun EditableProfileSection(
    title: String,
    items: MutableList<String>,
) {
    var isEditing by remember { mutableStateOf(false) }
    var newItem by remember { mutableStateOf("") }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "$title (${items.size})",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
                IconButton(onClick = { isEditing = !isEditing }, modifier = Modifier.size(24.dp)) {
                    Icon(
                        Icons.Filled.Edit,
                        contentDescription = "Edit $title",
                        modifier = Modifier.size(18.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Spacer(modifier = Modifier.height(8.dp))

            if (isEditing) {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    items.forEachIndexed { index, item ->
                        InputChip(
                            selected = false,
                            onClick = { items.removeAt(index) },
                            label = { Text(item, style = MaterialTheme.typography.bodyMedium) },
                            trailingIcon = {
                                Icon(
                                    Icons.Filled.Close,
                                    contentDescription = "Remove",
                                    modifier = Modifier.size(16.dp)
                                )
                            },
                        )
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(
                        value = newItem,
                        onValueChange = { newItem = it },
                        placeholder = { Text("Add new...") },
                        modifier = Modifier.weight(1f),
                        singleLine = true,
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    TextButton(onClick = {
                        if (newItem.isNotBlank()) {
                            items.add(newItem.trim())
                            newItem = ""
                        }
                    }) {
                        Text("Add")
                    }
                }
            } else {
                if (items.isEmpty()) {
                    Text(
                        "None — tap edit to add",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        items.forEach { item ->
                            AssistChip(
                                onClick = {},
                                label = { Text(item, style = MaterialTheme.typography.bodyMedium) }
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ProfileSection(title: String, items: List<String>) {
    if (items.isEmpty()) return

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
            )
            Spacer(modifier = Modifier.height(8.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items.forEach { item ->
                    AssistChip(
                        onClick = {},
                        label = { Text(item, style = MaterialTheme.typography.bodyMedium) }
                    )
                }
            }
        }
    }
}

private fun parseList(gson: Gson, json: String): List<String> {
    return try {
        gson.fromJson(json, Array<String>::class.java).toList()
    } catch (_: Exception) {
        emptyList()
    }
}

@Composable
private fun SkillGapSection(
    report: com.resumenews.app.data.remote.dto.SkillGapReport?,
    isLoading: Boolean,
    onFetch: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "AI Skill-Gap Report",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Compare your resume against trending tech news to find what you're missing.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))

            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            } else if (report == null) {
                Button(
                    onClick = onFetch,
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                ) {
                    Icon(Icons.Filled.AutoAwesome, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Generate Report")
                }
            } else {
                Text("Recommendation", style = MaterialTheme.typography.titleMedium)
                Text(report.recommendation, style = MaterialTheme.typography.bodyMedium)
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text("Missing Skills (Market Demand)", style = MaterialTheme.typography.titleMedium)
                Text(report.missingSkills.joinToString(", "), style = MaterialTheme.typography.bodyMedium)
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text("Resume Suggestions", style = MaterialTheme.typography.titleMedium)
                report.resumeSuggestions.forEach {
                    Text("• $it", style = MaterialTheme.typography.bodyMedium)
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                Button(
                    onClick = onFetch,
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text("Refresh Report")
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun PreferencesSection(
    prefs: com.resumenews.app.data.remote.dto.PreferencesDto,
    isSaving: Boolean,
    onSave: (List<String>, List<String>, String, Boolean, Int, Int) -> Unit
) {
    var seniority by remember(prefs.seniorityLevel) { mutableStateOf(prefs.seniorityLevel) }
    var notifyEnabled by remember(prefs.notifyEnabled) { mutableStateOf(prefs.notifyEnabled) }
    var quietStart by remember(prefs.quietHourStart) { mutableStateOf(prefs.quietHourStart.toString()) }
    var quietEnd by remember(prefs.quietHourEnd) { mutableStateOf(prefs.quietHourEnd.toString()) }
    
    val pTopics = remember(prefs.preferredTopics) { mutableStateListOf(*prefs.preferredTopics.toTypedArray()) }
    val bTopics = remember(prefs.blockedTopics) { mutableStateListOf(*prefs.blockedTopics.toTypedArray()) }

    Text(
        "Personalization & Preferences",
        style = MaterialTheme.typography.headlineSmall,
        modifier = Modifier.padding(vertical = 8.dp)
    )

    EditableProfileSection("Preferred Topics", pTopics)
    EditableProfileSection("Blocked Topics", bTopics)

    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("General Settings", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = seniority,
                onValueChange = { seniority = it },
                label = { Text("Seniority Level (student/junior/mid/senior/lead)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            Spacer(modifier = Modifier.height(16.dp))

            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("Enable Daily Notifications")
                androidx.compose.material3.Switch(
                    checked = notifyEnabled,
                    onCheckedChange = { notifyEnabled = it }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))
            Text("Quiet Hours (24h format)", style = MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                OutlinedTextField(
                    value = quietStart,
                    onValueChange = { quietStart = it },
                    label = { Text("Start") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                OutlinedTextField(
                    value = quietEnd,
                    onValueChange = { quietEnd = it },
                    label = { Text("End") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
            }

            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = {
                    onSave(
                        pTopics.toList(),
                        bTopics.toList(),
                        seniority,
                        notifyEnabled,
                        quietStart.toIntOrNull() ?: 22,
                        quietEnd.toIntOrNull() ?: 7
                    )
                },
                enabled = !isSaving,
                modifier = Modifier.align(Alignment.End)
            ) {
                if (isSaving) {
                    CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = MaterialTheme.colorScheme.onPrimary)
                    Spacer(modifier = Modifier.width(8.dp))
                }
                Text("Save Preferences")
            }
        }
    }
}
