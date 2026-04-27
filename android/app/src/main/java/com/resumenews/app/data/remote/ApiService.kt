package com.resumenews.app.data.remote

import com.resumenews.app.data.remote.dto.BookmarkRequest
import com.resumenews.app.data.remote.dto.DigestResponse
import com.resumenews.app.data.remote.dto.EditProfileBody
import com.resumenews.app.data.remote.dto.MarkReadRequest
import com.resumenews.app.data.remote.dto.NewsListResponse
import com.resumenews.app.data.remote.dto.ProfileDto
import com.resumenews.app.data.remote.dto.RefreshResponse
import com.resumenews.app.data.remote.dto.UploadResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @Multipart
    @POST("resume/upload")
    suspend fun uploadResume(
        @Part file: MultipartBody.Part,
        @Part("device_id") deviceId: RequestBody,
    ): UploadResponse

    @GET("resume/profile/{device_id}")
    suspend fun getProfile(
        @Path("device_id") deviceId: String,
    ): ProfileDto

    @PUT("resume/profile/{device_id}")
    suspend fun editProfile(
        @Path("device_id") deviceId: String,
        @Body body: EditProfileBody,
    ): UploadResponse

    @DELETE("resume/profile/{device_id}")
    suspend fun deleteProfile(
        @Path("device_id") deviceId: String,
    ): Map<String, Any>

    @GET("preferences/{device_id}/skill-gap")
    suspend fun getSkillGapReport(
        @Path("device_id") deviceId: String,
    ): com.resumenews.app.data.remote.dto.SkillGapResponse

    @GET("news/{device_id}")
    suspend fun getNewsUnread(
        @Path("device_id") deviceId: String,
        @Query("limit") limit: Int = 10,
        @Query("offset") offset: Int = 0,
    ): NewsListResponse

    @GET("news/{device_id}/all")
    suspend fun getNewsAll(
        @Path("device_id") deviceId: String,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
    ): NewsListResponse

    @POST("news/{device_id}/refresh")
    suspend fun refreshNews(
        @Path("device_id") deviceId: String,
    ): RefreshResponse

    @POST("news/{device_id}/mark-read")
    suspend fun markRead(
        @Path("device_id") deviceId: String,
        @Body body: MarkReadRequest,
    ): Map<String, Any>

    @GET("news/{device_id}/digest")
    suspend fun getDailyDigest(
        @Path("device_id") deviceId: String,
    ): DigestResponse

    @POST("bookmarks/{device_id}")
    suspend fun addBookmark(
        @Path("device_id") deviceId: String,
        @Body body: BookmarkRequest,
    ): Map<String, Any>

    @DELETE("bookmarks/{device_id}/{article_id}")
    suspend fun removeBookmark(
        @Path("device_id") deviceId: String,
        @Path("article_id") articleId: Int,
    ): Map<String, Any>
}
