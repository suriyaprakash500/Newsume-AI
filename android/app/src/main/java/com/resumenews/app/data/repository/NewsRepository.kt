package com.resumenews.app.data.repository

import android.content.Context
import android.provider.Settings
import com.resumenews.app.data.local.AppDatabase
import com.resumenews.app.data.local.entity.NewsArticleEntity
import com.resumenews.app.data.remote.RetrofitClient
import com.resumenews.app.data.remote.dto.ArticleDto
import com.resumenews.app.data.remote.dto.BookmarkRequest
import com.resumenews.app.data.remote.dto.DigestDto
import com.resumenews.app.data.remote.dto.MarkReadRequest
import kotlinx.coroutines.flow.Flow

class NewsRepository(context: Context) {

    private val dao = AppDatabase.getInstance(context).newsArticleDao()
    private val api = RetrofitClient.apiService
    private val deviceId: String = Settings.Secure.getString(
        context.contentResolver,
        Settings.Secure.ANDROID_ID
    )

    fun observeUnread(): Flow<List<NewsArticleEntity>> =
        dao.observeUnread(deviceId)

    fun observeBookmarked(): Flow<List<NewsArticleEntity>> =
        dao.observeBookmarked()

    suspend fun refreshFromServer(deviceId: String): Int {
        val refreshResult = api.refreshNews(deviceId)
        // Always sync from server after refresh — even if no NEW articles were
        // added (deduped), there may be existing unread articles not yet cached locally.
        fetchAndCacheArticles(deviceId)
        return refreshResult.newArticles
    }

    suspend fun syncNewsFromServer(deviceId: String) {
        fetchAndCacheArticles(deviceId)
    }

    suspend fun getUnreadCount(): Int =
        dao.getUnreadCount(deviceId)

    suspend fun markArticlesRead(deviceId: String, ids: List<Int>) {
        if (ids.isEmpty()) return
        dao.markRead(ids)
        try {
            api.markRead(deviceId, MarkReadRequest(ids))
        } catch (_: Exception) { }
    }

    suspend fun toggleBookmark(deviceId: String, articleId: Int, note: String = "") {
        dao.setBookmarked(articleId, true)
        try {
            api.addBookmark(deviceId, BookmarkRequest(articleId, note))
        } catch (_: Exception) { }
    }

    suspend fun removeBookmark(deviceId: String, articleId: Int) {
        dao.setBookmarked(articleId, false)
        try {
            api.removeBookmark(deviceId, articleId)
        } catch (_: Exception) { }
    }

    suspend fun getDailyDigest(deviceId: String): DigestDto {
        val response = api.getDailyDigest(deviceId)
        return response.digest
    }

    private suspend fun fetchAndCacheArticles(deviceId: String) {
        // Use /all endpoint so we always get articles regardless of backend read state.
        // Room tracks read state locally via the isRead field.
        val response = api.getNewsAll(deviceId, limit = 50, offset = 0)
        val entities = response.articles.map { it.toEntity(deviceId) }
        if (entities.isNotEmpty()) {
            dao.insertAll(entities)
        }
    }

    private fun ArticleDto.toEntity(deviceId: String) = NewsArticleEntity(
        id = id,
        deviceId = deviceId,
        title = title,
        description = description,
        url = url,
        imageUrl = imageUrl,
        sourceName = sourceName,
        sourceType = sourceType,
        sourceTrustScore = sourceTrustScore,
        author = author,
        publishedAt = publishedAt,
        relevanceScore = relevanceScore,
        matchedSkills = matchedSkills.joinToString(", "),
        careerWhy = careerWhy,
        careerWho = careerWho,
        careerAction = careerAction,
    )
}
