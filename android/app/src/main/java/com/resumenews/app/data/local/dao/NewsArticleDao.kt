package com.resumenews.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.resumenews.app.data.local.entity.NewsArticleEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface NewsArticleDao {

    @Query("SELECT * FROM news_articles WHERE deviceId = :deviceId AND isRead = 0 ORDER BY relevanceScore DESC")
    fun observeUnread(deviceId: String): Flow<List<NewsArticleEntity>>

    @Query("SELECT * FROM news_articles WHERE isBookmarked = 1 ORDER BY id DESC")
    fun observeBookmarked(): Flow<List<NewsArticleEntity>>

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertAll(articles: List<NewsArticleEntity>)

    @Query("UPDATE news_articles SET isRead = 1 WHERE id IN (:ids)")
    suspend fun markRead(ids: List<Int>)

    @Query("UPDATE news_articles SET isBookmarked = :bookmarked WHERE id = :articleId")
    suspend fun setBookmarked(articleId: Int, bookmarked: Boolean)

    @Query("SELECT COUNT(*) FROM news_articles WHERE deviceId = :deviceId AND isRead = 0")
    suspend fun getUnreadCount(deviceId: String): Int
}
