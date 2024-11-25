/**
 * 生成一个 UUID v4 的字符串
 * @returns {string} 一个符合 UUID v4 规范的字符串
 */
export function generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (char) => {
        const random = Math.random() * 16 | 0; // 生成一个 0-15 的随机数
        const value = char === 'x' ? random : (random & 0x3 | 0x8); // 确保符合 UUID v4 规范
        return value.toString(16); // 转成16进制
    });
}
