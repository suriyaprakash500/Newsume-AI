package com.resumenews.app.data.remote.dto

import com.google.gson.annotations.SerializedName

data class ProfileDto(
    @SerializedName("device_id") val deviceId: String = "",
    val name: String = "",
    val skills: List<String> = emptyList(),
    val certifications: List<String> = emptyList(),
    val experience: List<String> = emptyList(),
    val education: List<String> = emptyList(),
    val keywords: List<String> = emptyList(),
    val version: Int = 0,
    @SerializedName("resume_filename") val resumeFilename: String = "",
)

data class UploadResponse(
    val status: String = "",
    val profile: ProfileDto = ProfileDto(),
)

data class EditProfileBody(
    val skills: List<String>? = null,
    val certifications: List<String>? = null,
    val keywords: List<String>? = null,
)

data class SkillGapReport(
    @SerializedName("trending_skills") val trendingSkills: List<String> = emptyList(),
    @SerializedName("missing_skills") val missingSkills: List<String> = emptyList(),
    val recommendation: String = "",
    @SerializedName("resume_suggestions") val resumeSuggestions: List<String> = emptyList()
)

data class SkillGapResponse(
    val status: String = "",
    val report: SkillGapReport = SkillGapReport()
)

data class PreferencesDto(
    @SerializedName("preferred_topics") val preferredTopics: List<String> = emptyList(),
    @SerializedName("blocked_topics") val blockedTopics: List<String> = emptyList(),
    @SerializedName("seniority_level") val seniorityLevel: String = "mid",
    @SerializedName("notify_enabled") val notifyEnabled: Boolean = true,
    @SerializedName("quiet_hour_start") val quietHourStart: Int = 22,
    @SerializedName("quiet_hour_end") val quietHourEnd: Int = 7
)

data class PreferencesRequest(
    @SerializedName("preferred_topics") val preferredTopics: List<String>? = null,
    @SerializedName("blocked_topics") val blockedTopics: List<String>? = null,
    @SerializedName("seniority_level") val seniorityLevel: String? = null,
    @SerializedName("notify_enabled") val notifyEnabled: Boolean? = null,
    @SerializedName("quiet_hour_start") val quietHourStart: Int? = null,
    @SerializedName("quiet_hour_end") val quietHourEnd: Int? = null
)
