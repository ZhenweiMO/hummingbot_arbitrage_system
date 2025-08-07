/**
 * 隐藏敏感信息的工具函数
 * @param text 需要隐藏的文本
 * @param visibleChars 前后各显示的字符数，默认为4
 * @returns 隐藏中间部分的文本
 */
export const maskSensitiveInfo = (text: string, visibleChars: number = 4): string => {
  if (!text || text.length <= visibleChars * 2) {
    return text;
  }
  const start = text.substring(0, visibleChars);
  const end = text.substring(text.length - visibleChars);
  const middle = '*'.repeat(Math.min(text.length - visibleChars * 2, 8));
  return `${start}${middle}${end}`;
};

/**
 * 隐藏 API Key 的专用函数
 * @param apiKey API Key 字符串
 * @returns 隐藏中间部分的 API Key
 */
export const maskApiKey = (apiKey: string): string => {
  return maskSensitiveInfo(apiKey, 4);
};

/**
 * 隐藏 Secret Key 的专用函数
 * @param secretKey Secret Key 字符串
 * @returns 隐藏中间部分的 Secret Key
 */
export const maskSecretKey = (secretKey: string): string => {
  return maskSensitiveInfo(secretKey, 4);
};

/**
 * 隐藏钱包地址的专用函数
 * @param address 钱包地址
 * @returns 隐藏中间部分的地址
 */
export const maskAddress = (address: string): string => {
  return maskSensitiveInfo(address, 6);
}; 