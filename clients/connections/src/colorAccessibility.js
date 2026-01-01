/**
 * Color accessibility utilities for ensuring WCAG compliance
 */

function hexToRGB(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function sRGBToLinear(channel) {
  const c = channel / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

/**
 * Calculate relative luminance of a color
 * @param {string} color - Color in hex format (#RRGGBB or #RGB)
 * @returns {number} Relative luminance value between 0 and 1
 */
export function getRelativeLuminance(color) {
    if (!color) return 1; // Default to white luminance if no color
    if (color[0] !== '#') {
        throw new Error('Only hex color format is supported');
    }
    
    let hex = color;
    if (hex.length === 4) {
        hex = '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
    }
    
    const [r, g, b] = hexToRGB(hex);
    const [R, G, B] = [r, g, b].map(sRGBToLinear);
    
    return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

/**
 * Calculate contrast ratio between two colors
 * @param {string} color1 - First color in hex format
 * @param {string} color2 - Second color in hex format
 * @returns {number} Contrast ratio (1 to 21)
 */
export function getContrastRatio(color1, color2) {
    const lum1 = getRelativeLuminance(color1);
    const lum2 = getRelativeLuminance(color2);
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Ensure accessible color contrast between text and background
 * Returns an adjusted text color that meets WCAG AA standards (4.5:1 ratio)
 * @param {string|null} textColor - Desired text color in hex format
 * @param {string|null} bgColor - Background color in hex format
 * @returns {string|null} Adjusted text color or null if no adjustment needed
 */
export function ensureAccessibleContrast(textColor, bgColor) {
    if (!bgColor) return textColor; // No background color, use provided text color
    if (!textColor) {
        // No text color specified, choose black or white based on background
        const bgLuminance = getRelativeLuminance(bgColor);
        return bgLuminance > 0.5 ? '#000000' : '#ffffff';
    }
    
    const contrastRatio = getContrastRatio(textColor, bgColor);
    
    // WCAG AA requires 4.5:1 for normal text
    if (contrastRatio >= 4.5) {
        return textColor; // Contrast is good
    }
    
    // Contrast is poor, choose black or white based on which has better contrast
    const whiteContrast = getContrastRatio('#ffffff', bgColor);
    const blackContrast = getContrastRatio('#000000', bgColor);
    
    return whiteContrast > blackContrast ? '#ffffff' : '#000000';
}

/**
 * Adjust background color for selection state
 * Darkens light colors and lightens dark colors to indicate selection
 * @param {string} bgColor - Background color in hex format
 * @returns {string} Adjusted color for selected state
 */
export function getSelectedBackgroundColor(bgColor) {
    if (!bgColor) return '#3a3a3c'; // Default selected color
    
    const luminance = getRelativeLuminance(bgColor);
    
    // Parse hex color
    let hex = bgColor.replace('#', '');
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    
    let r = parseInt(hex.substr(0, 2), 16);
    let g = parseInt(hex.substr(2, 2), 16);
    let b = parseInt(hex.substr(4, 2), 16);
    
    // If light background, darken significantly
    // If dark background, lighten moderately
    if (luminance > 0.5) {
        // Light color - darken by 40%
        r = Math.round(r * 0.6);
        g = Math.round(g * 0.6);
        b = Math.round(b * 0.6);
    } else {
        // Dark color - lighten by 30%
        r = Math.min(255, Math.round(r + (255 - r) * 0.3));
        g = Math.min(255, Math.round(g + (255 - g) * 0.3));
        b = Math.min(255, Math.round(b + (255 - b) * 0.3));
    }
    
    // Convert back to hex
    const toHex = (val) => val.toString(16).padStart(2, '0');
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}
