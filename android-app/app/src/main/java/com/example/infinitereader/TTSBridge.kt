package com.example.infinitereader

import android.content.Context
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale

class TTSBridge(private val context: Context, private val webView: WebView) : TextToSpeech.OnInitListener {
    private var tts: TextToSpeech? = null
    private var isInitialized = false

    init {
        tts = TextToSpeech(context, this)
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            isInitialized = true
            tts?.language = Locale.US
            tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) {
                    val id = utteranceId?.toIntOrNull() ?: 0
                    webView.post {
                        webView.evaluateJavascript("window.onSpeechStart && window.onSpeechStart($id);", null)
                    }
                }

                override fun onDone(utteranceId: String?) {
                    val id = utteranceId?.toIntOrNull() ?: 0
                    webView.post {
                        webView.evaluateJavascript("window.onSpeechDone && window.onSpeechDone($id);", null)
                    }
                }

                @Deprecated("Deprecated in Java")
                override fun onError(utteranceId: String?) {
                    val id = utteranceId?.toIntOrNull() ?: 0
                    webView.post {
                        webView.evaluateJavascript("window.onSpeechDone && window.onSpeechDone($id);", null)
                    }
                }
            })

            // Notify JavaScript that native voices are initialized and ready
            webView.post {
                webView.evaluateJavascript("window.onVoicesLoaded && window.onVoicesLoaded();", null)
            }
        } else {
            Log.e("TTSBridge", "TextToSpeech init failed with status: $status")
        }
    }

    @JavascriptInterface
    fun speak(text: String, sentenceId: Int) {
        if (!isInitialized) return
        val params = Bundle()
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, params, sentenceId.toString())
    }

    @JavascriptInterface
    fun stop() {
        tts?.stop()
    }

    @JavascriptInterface
    fun setRate(rate: Float) {
        tts?.setSpeechRate(rate)
    }

    @JavascriptInterface
    fun setPitch(pitch: Float) {
        tts?.setPitch(pitch)
    }

    @JavascriptInterface
    fun setVoice(voiceName: String): Boolean {
        val voiceList = tts?.voices
        if (voiceList != null) {
            val matchedVoice = voiceList.find { it.name == voiceName }
            if (matchedVoice != null) {
                tts?.voice = matchedVoice
                tts?.language = matchedVoice.locale
                Log.d("TTSBridge", "Successfully set voice to: $voiceName (${matchedVoice.locale})")
                return true
            }
        }
        return false
    }

    @JavascriptInterface
    fun getVoicesJson(): String {
        val array = JSONArray()
        val voices = tts?.voices
        if (voices != null) {
            // Sort so english and natural voices are prioritized
            val sortedVoices = voices.sortedWith(compareBy({ it.locale.language != "en" }, { it.name }))
            for (v in sortedVoices) {
                val obj = JSONObject()
                obj.put("name", v.name)
                obj.put("locale", "${v.locale.displayLanguage} (${v.locale.country})")
                obj.put("isNetwork", v.isNetworkConnectionRequired)
                array.put(obj)
            }
        }
        return array.toString()
    }

    @JavascriptInterface
    fun getNovelDataJson(): String {
        return try {
            context.assets.open("novel_data.json").bufferedReader().use { it.readText() }
        } catch (e: Exception) {
            "{}"
        }
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
    }
}
