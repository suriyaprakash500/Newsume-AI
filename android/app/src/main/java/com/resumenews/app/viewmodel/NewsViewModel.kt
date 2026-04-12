package com.resumenews.app.viewmodel

import android.app.Application
import android.provider.Settings
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.resumenews.app.data.local.entity.NewsArticleEntity
import com.resumenews.app.data.remote.dto.DigestDto
import com.resumenews.app.data.repository.NewsRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class NewsUiState(
    val isRefreshing: Boolean = false,
    val error: String? = null,
    val newCount: Int = 0,
    val digest: DigestDto? = null,
    val isDigestLoading: Boolean = false,
    val isCaughtUp: Boolean = false
)

class NewsViewModel(application: Application) : AndroidViewModel(application) {

    private val repo = NewsRepository(application)

    val deviceId: String = Settings.Secure.getString(
        application.contentResolver,
        Settings.Secure.ANDROID_ID
    )

    val articles: StateFlow<List<NewsArticleEntity>> = repo.observeUnread()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000L), emptyList())

    val bookmarked: StateFlow<List<NewsArticleEntity>> = repo.observeBookmarked()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000L), emptyList())

    private val _uiState = MutableStateFlow(NewsUiState())
    val uiState: StateFlow<NewsUiState> = _uiState.asStateFlow()

    fun refreshNews() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true, error = null)
            try {
                val count = repo.refreshFromServer(deviceId)
                val unread = repo.getUnreadCount()
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    newCount = count,
                    isCaughtUp = unread == 0,
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    error = e.message ?: "Refresh failed"
                )
            }
        }
    }

    fun syncFromServer() {
        viewModelScope.launch {
            try {
                repo.syncNewsFromServer(deviceId)
                val unread = repo.getUnreadCount()
                _uiState.value = _uiState.value.copy(isCaughtUp = unread == 0)
            } catch (_: Exception) { }
        }
    }

    fun markRead(ids: List<Int>) {
        viewModelScope.launch {
            repo.markArticlesRead(deviceId, ids)
        }
    }

    fun toggleBookmark(articleId: Int, note: String = "") {
        viewModelScope.launch {
            repo.toggleBookmark(deviceId, articleId, note)
        }
    }

    fun removeBookmark(articleId: Int) {
        viewModelScope.launch {
            repo.removeBookmark(deviceId, articleId)
        }
    }

    fun loadDigest() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isDigestLoading = true)
            try {
                val digest = repo.getDailyDigest(deviceId)
                _uiState.value = _uiState.value.copy(
                    isDigestLoading = false,
                    digest = digest,
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isDigestLoading = false,
                    error = e.message ?: "Digest failed"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
