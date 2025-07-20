import type { MenuItem } from '@/types/menu-items.types';

export interface ParsedOrderItem {
  name: string;
  quantity: number;
  customizations?: string[];
  price?: number;
}

export interface OrderParseResult {
  items: ParsedOrderItem[];
  totalPrice?: number;
  success: boolean;
  message?: string;
}

export class OrderParser {
  /**
   * Parse chatbot response to extract order items
   */
  static parseOrderFromResponse(response: string): OrderParseResult {
    const items: ParsedOrderItem[] = [];
    let totalPrice = 0;
    
    // Common patterns for order confirmation (ordered from most specific to least specific)
    const orderPatterns = [
      // Pattern 1: Bullet points with quantities (most specific)
      /[-•]\s*I've added (\d+)\s+(.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /[-•]\s*Added (\d+)\s+(.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /[-•]\s*I've added (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /[-•]\s*Added (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      
      // Pattern 2: Multiple items with "and" or "&"
      /I've added (.+?)\s+and\s+(.+?)\s+to your cart/i,
      /Added (.+?)\s+and\s+(.+?)\s+to your cart/i,
      /I've added (.+?)\s*&\s*(.+?)\s+to your cart/i,
      /Added (.+?)\s*&\s*(.+?)\s+to your cart/i,
      
      // Pattern 3: Specific patterns with "the" and price info
      /I've added the (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /Added the (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      
      // Pattern 4: General patterns (least specific)
      /I've added (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /Added (.+?)(?:\s*\([^)]*\))?\s+to your cart/i,
      /I've added (.+?) to your cart/i,
      /Added (.+?) to your cart/i,
    ];

    // Quantity patterns
    const quantityPatterns = [
      /(\d+)\s*x\s*(.+)/i,
      /(\d+)\s*of\s*(.+)/i,
      /^(\d+)\s+(.+)$/i,  // Only match at start of string
    ];

    // Price patterns
    const pricePatterns = [
      /\$(\d+\.?\d*)/g,
      /₱(\d+\.?\d*)/g,
      /(\d+\.?\d*)\s*(?:dollars?|pesos?)/i,
    ];

    // Clean up item text by removing price information
    const cleanItemText = (text: string): string => {
      // Remove price patterns from the text
      return text
        .replace(/\$(\d+\.?\d*)/g, '')
        .replace(/₱(\d+\.?\d*)/g, '')
        .replace(/\((\d+\.?\d*)\)/g, '')
        .replace(/\(₱(\d+\.?\d*)\)/g, '')  // Handle ₱ symbol in parentheses
        .replace(/\s+/g, ' ')
        .trim();
    };

    let foundItems = false;
    const processedTexts = new Set<string>(); // Track processed text to avoid duplicates

    // Try to extract items from response
    for (const pattern of orderPatterns) {
      const matches = response.match(pattern);
      if (matches) {
        // Handle multiple items (patterns with "and" or "&")
        if (matches.length > 2) {
          // Multiple items pattern
          for (let i = 1; i < matches.length; i++) {
            const itemText = matches[i].trim();
            const parsedItem = this.parseSingleItem(itemText, quantityPatterns, pricePatterns, cleanItemText);
            if (parsedItem && !processedTexts.has(itemText)) {
              items.push(parsedItem);
              processedTexts.add(itemText);
            }
          }
        } else {
          // Single item pattern
          const itemText = matches[1].trim();
          const parsedItem = this.parseSingleItem(itemText, quantityPatterns, pricePatterns, cleanItemText);
          if (parsedItem && !processedTexts.has(itemText)) {
            items.push(parsedItem);
            processedTexts.add(itemText);
          }
        }
        
        foundItems = true;
        break; // Stop after first successful match to avoid duplicates
      }
    }
    
    // If we found items, also look for additional bullet points (only if no items found in main patterns)
    if (!foundItems) {
      // Look for bullet points that might have been missed
      const bulletPatterns = [
        /[-•]\s*I've added (\d+)\s+(.+?)(?:\s*\([^)]*\))?\s+to your cart/gi,
        /[-•]\s*Added (\d+)\s+(.+?)(?:\s*\([^)]*\))?\s+to your cart/gi,
        /[-•]\s*I've added (.+?)(?:\s*\([^)]*\))?\s+to your cart/gi,
        /[-•]\s*Added (.+?)(?:\s*\([^)]*\))?\s+to your cart/gi,
      ];
      
      for (const pattern of bulletPatterns) {
        const allMatches = response.matchAll(pattern);
        for (const match of allMatches) {
          if (match.length >= 2) {
            const quantity = match[1] ? parseInt(match[1]) : 1;
            const itemText = match[2] || match[1];
            const parsedItem = this.parseSingleItem(itemText, quantityPatterns, pricePatterns, cleanItemText);
            if (parsedItem && !processedTexts.has(itemText)) {
              // Override quantity if it was captured in the regex
              if (match[1] && !isNaN(parseInt(match[1]))) {
                parsedItem.quantity = quantity;
              }
              items.push(parsedItem);
              processedTexts.add(itemText);
            }
          }
        }
      }
    }

    // If no specific patterns found, try to extract from general text
    if (!foundItems) {
      // Look for menu items mentioned in the response
      const menuItemPatterns = [
        /(?:I recommend|You might like|Try the|How about|Consider)\s+(.+?)(?:\s|$|\.)/gi,
        /(?:You can order|You can get|Available options include)\s+(.+?)(?:\s|$|\.)/gi,
      ];

      for (const pattern of menuItemPatterns) {
        const matches = response.matchAll(pattern);
        for (const match of matches) {
          const itemName = match[1].trim();
          if (itemName && itemName.length > 2) {
            items.push({
              name: itemName,
              quantity: 1,
            });
          }
        }
      }
    }

    // Calculate total price if prices are available
    if (items.length > 0) {
      totalPrice = items.reduce((sum, item) => {
        return sum + (item.price || 0) * item.quantity;
      }, 0);
    }

    return {
      items,
      totalPrice: totalPrice > 0 ? totalPrice : undefined,
      success: items.length > 0,
      message: items.length > 0 
        ? `Found ${items.length} item(s) to add to cart`
        : 'No items found in response'
    };
  }

  /**
   * Parse a single item text to extract name, quantity, and price
   */
  private static parseSingleItem(
    itemText: string,
    quantityPatterns: RegExp[],
    pricePatterns: RegExp[],
    cleanItemText: (text: string) => string
  ): ParsedOrderItem | null {
    // Try to extract quantity
    let quantity = 1;
    let itemName = itemText;
    
    for (const qtyPattern of quantityPatterns) {
      const qtyMatch = itemText.match(qtyPattern);
      if (qtyMatch) {
        quantity = parseInt(qtyMatch[1]);
        itemName = qtyMatch[2].trim();
        break;
      }
    }

    // Try to extract price
    let price = undefined;
    for (const pricePattern of pricePatterns) {
      const priceMatch = itemText.match(pricePattern);
      if (priceMatch) {
        price = parseFloat(priceMatch[1]);
        break;
      }
    }

    // Clean the item name by removing price information
    const cleanedItemName = cleanItemText(itemName);
    
    // Only return if the cleaned name is not empty and not just punctuation
    if (cleanedItemName && cleanedItemName.length > 1 && !/^[^\w\s]*$/.test(cleanedItemName)) {
      return {
        name: cleanedItemName,
        quantity,
        price,
      };
    }
    
    return null;
  }

  /**
   * Find matching menu items from available menu
   */
  static findMatchingMenuItems(
    parsedItems: ParsedOrderItem[], 
    availableMenuItems: MenuItem[]
  ): { matched: MenuItem[]; unmatched: string[] } {
    const matched: MenuItem[] = [];
    const unmatched: string[] = [];

    for (const parsedItem of parsedItems) {
      // Try to find exact match first
      let found = availableMenuItems.find(item => 
        item.name.toLowerCase() === parsedItem.name.toLowerCase()
      );

      // If not found, try partial match
      if (!found) {
        found = availableMenuItems.find(item => 
          item.name.toLowerCase().includes(parsedItem.name.toLowerCase()) ||
          parsedItem.name.toLowerCase().includes(item.name.toLowerCase())
        );
      }

      // If still not found, try fuzzy match
      if (!found) {
        found = availableMenuItems.find(item => 
          this.calculateSimilarity(item.name.toLowerCase(), parsedItem.name.toLowerCase()) > 0.7
        );
      }

      if (found) {
        matched.push(found);
      } else {
        unmatched.push(parsedItem.name);
      }
    }

    return { matched, unmatched };
  }

  /**
   * Calculate string similarity using simple algorithm
   */
  private static calculateSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const distance = this.levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  }

  /**
   * Calculate Levenshtein distance between two strings
   */
  private static levenshteinDistance(str1: string, str2: string): number {
    const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));

    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;

    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1, // deletion
          matrix[j - 1][i] + 1, // insertion
          matrix[j - 1][i - 1] + indicator // substitution
        );
      }
    }
    return matrix[str2.length][str1.length];
  }
} 