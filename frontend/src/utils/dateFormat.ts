/**
 * 格式化ISO时间字符串为自定义格式
 * @param isoString ISO格式的时间字符串
 * @param format 输出格式 (可选，默认为 'YYYY-MM-DD HH:mm:ss')
 * @returns 格式化后的时间字符串
 */
export function formatISODate(
  isoString: string,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  try {
    const date = new Date(isoString);
    
    // 检查是否为有效日期
    if (isNaN(date.getTime())) {
      throw new Error('无效的日期格式');
    }

    const formatMap: Record<string, string> = {
      YYYY: date.getFullYear().toString(),
      MM: (date.getMonth() + 1).toString().padStart(2, '0'),
      DD: date.getDate().toString().padStart(2, '0'),
      HH: date.getHours().toString().padStart(2, '0'),
      mm: date.getMinutes().toString().padStart(2, '0'),
      ss: date.getSeconds().toString().padStart(2, '0')
    };

    return format.replace(/(YYYY|MM|DD|HH|mm|ss)/g, match => formatMap[match]);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return isoString; // 发生错误时返回原始字符串
  }
}

/**
 * 将任意时间格式转换为标准格式 (YYYY-MM-DD HH:mm:ss)
 * @param dateInput 日期输入 (字符串、Date对象或时间戳)
 * @returns 格式化后的时间字符串
 */
export function standardizeDate(
  dateInput: string | Date | number
): string {
  try {
    const date = new Date(dateInput);
    
    // 检查是否为有效日期
    if (isNaN(date.getTime())) {
      throw new Error('无效的日期格式');
    }

    return formatISODate(date.toISOString());
  } catch (error) {
    console.error('日期标准化错误:', error);
    return String(dateInput);
  }
}

/**
 * 检查日期字符串是否为ISO格式
 * @param dateString 日期字符串
 * @returns 是否为ISO格式
 */
export function isISODate(dateString: string): boolean {
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:?\d{2})?$/;
  return isoDatePattern.test(dateString);
}
