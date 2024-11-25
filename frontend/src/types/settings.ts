export type ThemeMode = 'light' | 'dark' | 'system'

export interface UserSettings {
  theme: ThemeMode
  fontSize: number
  enterToSend: boolean
  autoScroll: boolean
  showTimestamp: boolean
}

export interface SettingsState {
  settings: UserSettings
} 