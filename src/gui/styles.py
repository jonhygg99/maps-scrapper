"""
Custom styles and theme configuration for GUI
"""
import customtkinter as ctk


# Color scheme
COLORS = {
    'primary': '#1f6aa5',
    'secondary': '#144870',
    'success': '#2fa572',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'dark': '#2b2b2b',
    'light': '#f0f0f0',
    'bg_dark': '#1a1a1a',
    'bg_light': '#2b2b2b',
    'text_light': '#ffffff',
    'text_dark': '#000000',
    'text_secondary': '#999999',
    'border': '#444444',
}


# Fonts
FONTS = {
    'title': ('Arial', 20, 'bold'),
    'heading': ('Arial', 16, 'bold'),
    'subheading': ('Arial', 14, 'bold'),
    'normal': ('Arial', 12),
    'small': ('Arial', 10),
}


def apply_theme():
    """Apply custom theme to the application"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def get_button_style(variant='primary'):
    """
    Get button style configuration
    
    Args:
        variant: Button variant (primary, success, danger, warning)
    
    Returns:
        Dictionary with button style configuration
    """
    styles = {
        'primary': {
            'fg_color': COLORS['primary'],
            'hover_color': COLORS['secondary'],
        },
        'success': {
            'fg_color': COLORS['success'],
            'hover_color': '#27ae60',
        },
        'danger': {
            'fg_color': COLORS['danger'],
            'hover_color': '#c0392b',
        },
        'warning': {
            'fg_color': COLORS['warning'],
            'hover_color': '#e67e22',
        },
    }
    
    return styles.get(variant, styles['primary'])
