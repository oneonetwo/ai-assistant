import dayjs from 'dayjs'

export function formatDate(date: string | Date, format: string): string {
  return dayjs(date).format(format)
}