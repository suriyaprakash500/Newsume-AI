package com.resumenews.app.viewmodel

import android.app.Application
import android.net.Uri
import android.provider.Settings
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.resumenews.app.data.local.entity.UserProfileEntity
import com.resumenews.app.data.remote.dto.ProfileDto
import com.resumenews.app.data.repository.ResumeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class ResumeUiState(
    val isUploading: Boolean = false,
    val uploadSuccess: Boolean = false,
    val isSaving: Boolean = false,
    val saveSuccess: Boolean = false,
    val error: String? = null,
    val lastUploadedProfile: ProfileDto? = null,
    val isDeleting: Boolean = false,
    val skillGapReport: com.resumenews.app.data.remote.dto.SkillGapReport? = null,
    val isLoadingSkillGap: Boolean = false
)

class ResumeViewModel(application: Application) : AndroidViewModel(application) {

    private val repo = ResumeRepository(application)

    val deviceId: String = Settings.Secure.getString(
        application.contentResolver,
        Settings.Secure.ANDROID_ID
    )

    private val _uiState = MutableStateFlow(ResumeUiState())
    val uiState: StateFlow<ResumeUiState> = _uiState.asStateFlow()

    val profile: StateFlow<UserProfileEntity?> = repo.observeProfile(deviceId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000L), null)

    fun uploadResume(fileUri: Uri) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isUploading = true, uploadSuccess = false, error = null
            )
            try {
                val result = repo.uploadResume(getApplication(), deviceId, fileUri)
                _uiState.value = _uiState.value.copy(
                    isUploading = false,
                    uploadSuccess = true,
                    lastUploadedProfile = result,
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isUploading = false,
                    error = e.message ?: "Upload failed",
                )
            }
        }
    }

    fun clearUploadSuccess() {
        _uiState.value = _uiState.value.copy(uploadSuccess = false)
    }

    fun saveProfileEdits(
        skills: List<String>? = null,
        certifications: List<String>? = null,
        keywords: List<String>? = null,
    ) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSaving = true, saveSuccess = false)
            try {
                repo.editProfile(deviceId, skills, certifications, keywords)
                _uiState.value = _uiState.value.copy(isSaving = false, saveSuccess = true)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isSaving = false,
                    error = e.message ?: "Save failed"
                )
            }
        }
    }

    fun deleteProfile(context: android.content.Context) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isDeleting = true, error = null)
            try {
                repo.deleteProfile(context, deviceId)
                _uiState.value = ResumeUiState() // Reset entirely
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isDeleting = false,
                    error = e.message ?: "Delete failed"
                )
            }
        }
    }

    fun fetchSkillGapReport() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoadingSkillGap = true, error = null)
            try {
                val report = repo.getSkillGapReport(deviceId)
                _uiState.value = _uiState.value.copy(
                    isLoadingSkillGap = false,
                    skillGapReport = report
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoadingSkillGap = false,
                    error = e.message ?: "Failed to fetch skill gap report"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    fun clearSaveSuccess() {
        _uiState.value = _uiState.value.copy(saveSuccess = false)
    }
}
