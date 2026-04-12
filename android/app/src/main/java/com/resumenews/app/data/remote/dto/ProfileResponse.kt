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
