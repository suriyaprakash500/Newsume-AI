package com.resumenews.app.data.repository

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.google.gson.Gson
import com.resumenews.app.data.local.AppDatabase
import com.resumenews.app.data.local.entity.UserProfileEntity
import com.resumenews.app.data.remote.RetrofitClient
import com.resumenews.app.data.remote.dto.EditProfileBody
import com.resumenews.app.data.remote.dto.ProfileDto
import kotlinx.coroutines.flow.Flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class ResumeRepository(context: Context) {

    private val dao = AppDatabase.getInstance(context).userProfileDao()
    private val api = RetrofitClient.apiService
    private val gson = Gson()

    fun observeProfile(deviceId: String): Flow<UserProfileEntity?> =
        dao.observe(deviceId)

    suspend fun uploadResume(context: Context, deviceId: String, fileUri: Uri): ProfileDto {
        val contentResolver = context.contentResolver
        val bytes = contentResolver.openInputStream(fileUri)?.use { it.readBytes() }
            ?: throw IllegalStateException("Cannot read file")

        val fileName = resolveFileName(context, fileUri)
        val mimeType = contentResolver.getType(fileUri) ?: "application/octet-stream"

        val filePart = MultipartBody.Part.createFormData(
            "file",
            fileName,
            bytes.toRequestBody(mimeType.toMediaTypeOrNull())
        )
        val deviceIdPart = deviceId.toRequestBody("text/plain".toMediaTypeOrNull())

        val response = api.uploadResume(filePart, deviceIdPart)
        val profile = response.profile
        dao.upsert(profile.toEntity())
        return profile
    }

    suspend fun editProfile(
        deviceId: String,
        skills: List<String>?,
        certifications: List<String>?,
        keywords: List<String>?,
    ) {
        val body = EditProfileBody(
            skills = skills,
            certifications = certifications,
            keywords = keywords,
        )
        val response = api.editProfile(deviceId, body)
        dao.upsert(response.profile.toEntity())
    }

    suspend fun deleteProfile(context: Context, deviceId: String) {
        api.deleteProfile(deviceId)
        AppDatabase.getInstance(context).clearAllTables()
    }

    suspend fun getSkillGapReport(deviceId: String): com.resumenews.app.data.remote.dto.SkillGapReport {
        return api.getSkillGapReport(deviceId).report
    }

    suspend fun getPreferences(deviceId: String): com.resumenews.app.data.remote.dto.PreferencesDto {
        return api.getPreferences(deviceId)
    }

    suspend fun updatePreferences(
        deviceId: String,
        preferredTopics: List<String>? = null,
        blockedTopics: List<String>? = null,
        seniorityLevel: String? = null,
        notifyEnabled: Boolean? = null,
        quietHourStart: Int? = null,
        quietHourEnd: Int? = null
    ) {
        val request = com.resumenews.app.data.remote.dto.PreferencesRequest(
            preferredTopics, blockedTopics, seniorityLevel, notifyEnabled, quietHourStart, quietHourEnd
        )
        api.updatePreferences(deviceId, request)
    }

    private fun ProfileDto.toEntity() = UserProfileEntity(
        deviceId = deviceId,
        name = name,
        skills = gson.toJson(skills),
        certifications = gson.toJson(certifications),
        experience = gson.toJson(experience),
        education = gson.toJson(education),
        keywords = gson.toJson(keywords),
        version = version,
        resumeFilename = resumeFilename,
    )

    private fun resolveFileName(context: Context, uri: Uri): String {
        var name = "resume"
        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && cursor.moveToFirst()) {
                name = cursor.getString(idx)
            }
        }
        return name
    }
}
