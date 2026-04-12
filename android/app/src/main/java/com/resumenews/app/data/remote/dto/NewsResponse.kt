package com.resumenews.app.data.remote.dto

import com.google.gson.annotations.SerializedName

data class ArticleDto(
    val id: Int = 0,
    val title: String = "",
    val description: String = "",
    val url: String = "",
    @SerializedName("image_url") val imageUrl: String = "",
    @SerializedName("source_name") val sourceName: String = "",
    @SerializedName("source_type") val sourceType: String = "",
    @SerializedName("source_trust_score") val sourceTrustScore: Double = 0.5,
    val author: String = "",
    @SerializedName("published_at") val publishedAt: String = "",
    @SerializedName("relevance_score") val relevanceScore: Double = 0.0,
    @SerializedName("matched_skills") val matchedSkills: List<String> = emptyList(),
    @SerializedName("career_why") val careerWhy: String = "",
    @SerializedName("career_who") val careerWho: String = "",
    @SerializedName("career_action") val careerAction: String = "",
)

data class NewsListResponse(
    val count: Int = 0,
    @SerializedName("unread_total") val unreadTotal: Int = 0,
    val articles: List<ArticleDto> = emptyList(),
)

data class RefreshResponse(
    val status: String = "",
    @SerializedName("new_articles") val newArticles: Int = 0,
)

data class DigestDto(
    val bullets: List<String> = emptyList(),
    @SerializedName("recommended_action") val recommendedAction: String = "",
)

data class DigestResponse(
    val status: String = "",
    val digest: DigestDto = DigestDto(),
)

data class MarkReadRequest(
    @SerializedName("article_ids") val articleIds: List<Int>,
)

data class BookmarkRequest(
    @SerializedName("article_id") val articleId: Int,
    val note: String = "",
)
