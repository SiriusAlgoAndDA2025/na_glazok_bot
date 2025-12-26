"""
Generate architecture diagram for the Telegram Optical Illusion Bot
Minimal design with focus on AI
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Create figure with white background
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
fig.patch.set_facecolor('white')

# Color scheme
COLOR_BOT = '#AF7AC5'   # Purple
COLOR_AI = '#EC7063'    # Red
COLOR_MODEL = '#E74C3C' # Dark red
COLOR_OTHER = '#85929E' # Gray

def create_box(ax, x, y, width, height, text, color, subtitle='', fontsize=13):
    """Create a rounded rectangle box with text"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.12",
        facecolor=color,
        edgecolor='white',
        linewidth=3,
        alpha=0.95
    )
    ax.add_patch(box)

    # Main text
    y_offset = 0.15 if subtitle else 0
    ax.text(x + width/2, y + height/2 + y_offset, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight='bold',
            color='white')

    # Subtitle
    if subtitle:
        ax.text(x + width/2, y + height/2 - 0.2, subtitle,
                ha='center', va='center',
                fontsize=9,
                color='white', alpha=0.85)

def create_arrow(ax, x1, y1, x2, y2, label='', color='#666666'):
    """Create an arrow with optional label"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->,head_width=0.4,head_length=0.8',
        color=color,
        linewidth=2.5,
        alpha=0.7
    )
    ax.add_patch(arrow)

    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.15, label,
                ha='center', va='center',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.35', facecolor='white', alpha=0.95, edgecolor='#CCCCCC', linewidth=1.5))

# Title
ax.text(5, 9.4, 'AI-Powered Bot Architecture',
        ha='center', va='top',
        fontsize=19, fontweight='bold',
        color='#2C3E50')

# Top layer
create_box(ax, 1.5, 7.8, 2, 0.8, 'Bot', COLOR_BOT, fontsize=12)
create_box(ax, 6.5, 7.8, 2, 0.8, 'Database', COLOR_OTHER, fontsize=12)

# Main AI Service
create_box(ax, 2.5, 5.8, 5, 1.4, 'AIService', COLOR_AI, 'ai_service.py', fontsize=15)

# AI Models
create_box(ax, 1, 3.5, 3.5, 1.2, 'gemini-2.5-flash-lite', COLOR_MODEL, 'Prompt Generation', fontsize=12)
create_box(ax, 5.5, 3.5, 3.5, 1.2, 'gpt-image-1-mini', COLOR_MODEL, 'Image Generation', fontsize=13)

# Model inputs/outputs - minimal
ax.text(2.75, 4.0, 'answer → prompt', ha='center', fontsize=8.5, color='white')
ax.text(7.25, 4.0, 'prompt → image', ha='center', fontsize=8.5, color='white')

# Arrows
create_arrow(ax, 3.5, 7.8, 4.5, 7.2)
create_arrow(ax, 5.5, 7.2, 6.5, 7.8)
create_arrow(ax, 3.5, 5.8, 2.75, 4.7, '1')
create_arrow(ax, 6.5, 5.8, 7.25, 4.7, '2')

# Workflow at bottom
ax.text(5, 2.3, 'Bot → AIService → Models (gemini-2.5, gpt-image) → Return Result',
        ha='center', va='center',
        fontsize=11,
        color='#34495E',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', alpha=0.9, edgecolor='#CCCCCC', linewidth=1.5))

# Tech stack
ax.text(5, 1.5, 'Python 3.14+  |  aiogram  |  OpenAI SDK  |  asyncio',
        ha='center', va='center',
        fontsize=10, fontweight='bold',
        color='#2C3E50')

# Small note
ax.text(5, 0.8, 'Two-step AI pipeline: text generation → image generation',
        ha='center', va='center',
        fontsize=9, style='italic',
        color='#7F8C8D')

plt.tight_layout()
plt.savefig('/Users/imaximus3/personal/na_glazok_bot/python_telegram_bot/architecture_diagram.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Architecture diagram saved to: architecture_diagram.png")
