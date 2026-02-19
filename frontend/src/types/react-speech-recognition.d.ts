/**
 * Type declarations for react-speech-recognition
 * Since @types/react-speech-recognition doesn't exist on npm
 */

declare module 'react-speech-recognition' {
  import { ReactNode } from 'react'

  export interface UseSpeechRecognitionOptions {
    commands?: Array<{
      command: string | string[]
      callback: (command?: string) => void
    }>
    resetTranscriptTimeout?: number
    abortTranscript?: boolean
  }

  export interface UseSpeechRecognitionReturn {
    transcript: string
    interimTranscript: string
    finalTranscript: string
    resetTranscript: () => void
    listening: boolean
    isMicrophoneAvailable: boolean
    isListening: boolean
    browserSupportsSpeechRecognition: boolean
  }

  export function useSpeechRecognition(
    options?: UseSpeechRecognitionOptions
  ): UseSpeechRecognitionReturn

  export class SpeechRecognition {
    static startListening(options?: {
      continuous?: boolean
      interimResults?: boolean
      language?: string
    }): Promise<void>
    static stopListening(): Promise<void>
    static abortListening(): void
    static getRecognition(): SpeechRecognitionAPI
    static applyPolyfill(instance: any): void
  }

  export interface SpeechRecognitionAPI {
    continuous?: boolean
    interimResults?: boolean
    lang: string
    maxAlternatives?: number
    onstart?: () => void
    onend?: () => void
    onerror?: (event: any) => void
    onresult?: (event: any) => void
    onspeechend?: () => void
    abort?: () => void
    stop?: () => void
    start?: () => void
  }

  export default class SpeechRecognition {
    static startListening(options?: {
      continuous?: boolean
      interimResults?: boolean
      language?: string
    }): Promise<void>
    static stopListening(): Promise<void>
    static abortListening(): void
    static getRecognition(): SpeechRecognitionAPI
  }
}
