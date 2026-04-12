package com.resumenews.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_profiles")
data class UserProfileEntity(
    @PrimaryKey val deviceId: String,
    val name: String = "",
    val skills: String = "[]",
    val certifications: String = "[]",
    val experience: String = "[]",
    val education: String = "[]",
    val keywords: String = "[]",
    val version: Int = 0,
    val resumeFilename: String = "",
)
