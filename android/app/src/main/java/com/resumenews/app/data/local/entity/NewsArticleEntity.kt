package com.resumenews.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "news_articles")
data class NewsArticleEntity(
    @PrimaryKey val id: Int,
    val deviceId: String = "",
    val title: String = "",
    val description: String = "",
    val url: String = "",
    val imageUrl: String = "",
    val sourceName: String = "",
    val sourceType: String = "",
    val sourceTrustScore: Double = 0.5,
    val author: String = "",
    val publishedAt: String = "",
    val relevanceScore: Double = 0.0,
    val matchedSkills: String = "",
    val careerWhy: String = "",
    val careerWho: String = "",
    val careerAction: String = "",
    val isBookmarked: Boolean = false,
    val isRead: Boolean = false,
)
