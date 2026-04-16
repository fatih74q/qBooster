#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                    qBooster v0.2 Beta                       ║
║         Windows Sistem Kaynak Optimizasyonu                  ║
║  Full HD Neon Logo + 11 Dil + DNS/Junk/RAM/CPU Optimizer    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import math
import ctypes
import ctypes.wintypes as wintypes
import winreg
import psutil
import subprocess
import threading
import shutil
import glob
import tempfile
import random
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import customtkinter as ctk


# ═══════════════════════════════════════════════════════════════
# SABİTLER
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# DOSYA YOLLARI VE LOGO AYARLARI
# ═══════════════════════════════════════════════════════════════
import sys
from PIL import Image

def resource_path(relative_path):
    try:
        # PyInstaller geçici klasör yolu (_MEIPASS)
        base_path = sys._MEIPASS
    except Exception:
        # Normal Python çalışma dizini
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

LOGO_FILE_NAME = "logo.png" 

LOGO_PATH = resource_path(LOGO_FILE_NAME)

# ═══════════════════════════════════════════════════════════════
# ANA UYGULAMA SINIFI
# ═══════════════════════════════════════════════════════════════

APP_NAME = "qBooster"
APP_VERSION = "v0.2 Beta"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".qbooster")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "booster.log")
RESTORE_FILE = os.path.join(CONFIG_DIR, "restore_state.json")
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
LOGO_HD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_hd.png")


# ═══════════════════════════════════════════════════════════════
# FULL HD LOGO ÜRETİCİ — 1920x1920 NEON ŞİMŞEK
# ═══════════════════════════════════════════════════════════════
# Dosya: logo_hd.png (1920x1920) → otomatik oluşturulur
# Küçük versiyonlar runtime'da resize edilir:
#   - Header ikonu: 52x52
#   - Taskbar ikonu: 256x256
#   - Splash/About: 256x256
#
# Kendi logonuzu kullanmak için:
#   1. 1920x1920 PNG hazırlayın
#   2. Arka plan: koyu mavi radyal gradient
#   3. Şimşek: neon yeşil (#39ff14) + glow
#   4. "logo_hd.png" olarak qbooster.py yanına kaydedin
# ═══════════════════════════════════════════════════════════════


def generate_logo_hd(size=1920) -> Image.Image:
    """
    1920x1920 Full HD neon yeşil şimşek logosu üretir.
    4x supersampling + Gaussian blur glow + radyal gradient.
    """

    # ── 4x Supersampling için büyük canvas ──
    ss = 4  # Supersampling faktörü
    work_size = size * ss  # 7680x7680
    center = work_size // 2
    radius = work_size // 2 - (work_size // 40)

    img = Image.new("RGBA", (work_size, work_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ═══════════════════════════════════════
    # KATMAN 1: RADYAL GRADİENT ARKA PLAN
    # ═══════════════════════════════════════
    # İç: koyu lacivert (#0a1628) → Dış: siyaha yakın (#040810)

    for r in range(radius, 0, -max(1, work_size // 800)):
        ratio = r / radius
        # Merkez açık, kenar koyu
        red = int(10 * ratio + 4 * (1 - ratio))
        green = int(22 * ratio + 8 * (1 - ratio))
        blue = int(40 * ratio + 16 * (1 - ratio))

        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(red, green, blue, 255),
        )

    # ═══════════════════════════════════════
    # KATMAN 2: DIŞ HALKA — NEON GLOW
    # ═══════════════════════════════════════

    ring_width = work_size // 60

    # Dış glow halkası (geniş, yarı saydam yeşil)
    for i in range(30, 0, -1):
        glow_r = radius + (i * ring_width // 8)
        glow_alpha = max(3, 40 - i)
        draw.ellipse(
            [center - glow_r, center - glow_r,
             center + glow_r, center + glow_r],
            outline=(57, 255, 20, glow_alpha),
            width=ring_width // 2,
        )

    # Ana dış halka (parlak neon yeşil)
    draw.ellipse(
        [center - radius, center - radius,
         center + radius, center + radius],
        outline=(57, 255, 20, 220),
        width=ring_width,
    )

    # İç ince halka (beyazımsı yeşil — parlama)
    inner_ring_r = radius - ring_width
    draw.ellipse(
        [center - inner_ring_r, center - inner_ring_r,
         center + inner_ring_r, center + inner_ring_r],
        outline=(180, 255, 180, 60),
        width=ring_width // 4,
    )

    # ═══════════════════════════════════════
    # KATMAN 3: ENERJİ PARTİKÜLLERİ
    # ═══════════════════════════════════════
    # Halka çevresinde rastgele küçük parıltılar

    random.seed(42)  # Deterministik sonuç
    for _ in range(48):
        angle = random.uniform(0, 2 * math.pi)
        dist = radius + random.uniform(-ring_width * 3, ring_width * 3)
        px = center + int(dist * math.cos(angle))
        py = center + int(dist * math.sin(angle))
        p_size = random.randint(work_size // 200, work_size // 80)
        p_alpha = random.randint(40, 180)

        # Partikül glow
        for g in range(6, 0, -1):
            gs = p_size + g * (work_size // 300)
            ga = max(5, p_alpha // (g + 1))
            draw.ellipse(
                [px - gs, py - gs, px + gs, py + gs],
                fill=(57, 255, 20, ga),
            )

        # Partikül çekirdek
        draw.ellipse(
            [px - p_size, py - p_size, px + p_size, py + p_size],
            fill=(200, 255, 200, p_alpha),
        )

    # ═══════════════════════════════════════
    # KATMAN 4: ŞİMŞEK BOLT — NEON GLOW
    # ═══════════════════════════════════════

    # Şimşek koordinatları (normalize 0-1)
    bolt_points_norm = [
        (0.56, 0.12),   # Üst sağ
        (0.28, 0.46),   # Sol orta
        (0.46, 0.46),   # İç köşe sol
        (0.22, 0.50),   # Sol çıkıntı
        (0.44, 0.50),   # İç köşe
        (0.32, 0.88),   # Alt sol uç
        (0.76, 0.36),   # Sağ orta
        (0.56, 0.36),   # İç köşe sağ
        (0.78, 0.32),   # Sağ çıkıntı
        (0.58, 0.32),   # İç köşe
        (0.68, 0.12),   # Üst sol
    ]

    bolt_points = [
        (int(x * work_size), int(y * work_size))
        for x, y in bolt_points_norm
    ]

    # ── 4.1: Geniş dış glow (25 katman) ──
    for offset in range(25, 0, -1):
        glow_alpha = max(3, 50 - offset * 2)
        expanded = []
        cx_bolt = sum(p[0] for p in bolt_points) / len(bolt_points)
        cy_bolt = sum(p[1] for p in bolt_points) / len(bolt_points)

        scale = 1.0 + (offset * 0.008)
        for px, py in bolt_points:
            nx = cx_bolt + (px - cx_bolt) * scale
            ny = cy_bolt + (py - cy_bolt) * scale
            expanded.append((nx, ny))

        draw.polygon(expanded, fill=(57, 255, 20, glow_alpha))

    # ── 4.2: Ana şimşek gövdesi ──
    draw.polygon(bolt_points, fill=(57, 255, 20, 255))

    # ── 4.3: İç gradient (açık yeşil → beyaz merkez) ──
    inner_bolt_norm = [
        (0.55, 0.17),
        (0.34, 0.45),
        (0.47, 0.45),
        (0.30, 0.49),
        (0.45, 0.49),
        (0.38, 0.78),
        (0.68, 0.38),
        (0.55, 0.38),
        (0.70, 0.34),
        (0.57, 0.34),
        (0.64, 0.17),
    ]
    inner_bolt = [
        (int(x * work_size), int(y * work_size))
        for x, y in inner_bolt_norm
    ]
    draw.polygon(inner_bolt, fill=(180, 255, 180, 160))

    # ── 4.4: Parlak çekirdek çizgi ──
    core_bolt_norm = [
        (0.555, 0.22),
        (0.39, 0.445),
        (0.475, 0.445),
        (0.37, 0.485),
        (0.455, 0.485),
        (0.42, 0.68),
        (0.62, 0.395),
        (0.555, 0.395),
        (0.64, 0.355),
        (0.575, 0.355),
        (0.61, 0.22),
    ]
    core_bolt = [
        (int(x * work_size), int(y * work_size))
        for x, y in core_bolt_norm
    ]
    draw.polygon(core_bolt, fill=(230, 255, 230, 100))

    # ═══════════════════════════════════════
    # KATMAN 5: IŞIK YANSIMALARI
    # ═══════════════════════════════════════

    # Üst sol köşedeki yansıma (lens flare efekti)
    flare_r = work_size // 6
    flare_x = center - work_size // 5
    flare_y = center - work_size // 4

    for f in range(20, 0, -1):
        fr = flare_r + f * (work_size // 100)
        fa = max(2, 15 - f)
        draw.ellipse(
            [flare_x - fr, flare_y - fr, flare_x + fr, flare_y + fr],
            fill=(57, 255, 20, fa),
        )

    # ═══════════════════════════════════════
    # KATMAN 6: İÇ AMBIYANS IŞIĞI
    # ═══════════════════════════════════════

    # Şimşeğin etrafındaki ambient glow
    ambient_r = work_size // 3
    for a in range(15, 0, -1):
        ar = ambient_r + a * (work_size // 60)
        aa = max(2, 12 - a)
        cx_bolt = int(0.50 * work_size)
        cy_bolt = int(0.50 * work_size)
        draw.ellipse(
            [cx_bolt - ar, cy_bolt - ar, cx_bolt + ar, cy_bolt + ar],
            fill=(20, 80, 20, aa),
        )

    # ═══════════════════════════════════════
    # SON: SUPERSAMPLING DOWNSAMPLE + BLUR
    # ═══════════════════════════════════════

    # Hafif Gaussian blur (glow yumuşatma)
    img = img.filter(ImageFilter.GaussianBlur(radius=work_size // 500))

    # 4x downsample → anti-aliased final
    img = img.resize((size, size), Image.LANCZOS)

    return img


def generate_logo_small(size=64) -> Image.Image:
    """Küçük boyutlar için optimize edilmiş basit logo."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = 2
    draw.ellipse([pad, pad, size - pad, size - pad],
                 fill=(10, 22, 40, 255), outline=(57, 255, 20, 180), width=2)
    bolt = [(0.55, 0.10), (0.30, 0.45), (0.48, 0.45),
            (0.35, 0.90), (0.75, 0.38), (0.55, 0.38), (0.68, 0.10)]
    pts = [(int(x * size), int(y * size)) for x, y in bolt]
    for o in range(4, 0, -1):
        draw.polygon([(x + o * 0.3, y + o * 0.3) for x, y in pts],
                     fill=(57, 255, 20, max(10, 60 - o * 12)))
    draw.polygon(pts, fill=(57, 255, 20, 255))
    return img


def get_or_create_logo() -> dict:
    """
    Logo dosyalarını yükler veya oluşturur.
    Returns: {"hd": Image, "header": Image, "icon": Image}
    """
    logos = {}

    # Full HD logo
    if os.path.exists(LOGO_HD_PATH):
        logos["hd"] = Image.open(LOGO_HD_PATH)
    else:
        print("Generating Full HD logo (1920x1920)... This may take 10-15 seconds.")
        logos["hd"] = generate_logo_hd(1920)
        logos["hd"].save(LOGO_HD_PATH, "PNG", quality=100)
        print(f"Logo saved: {LOGO_HD_PATH}")

    # Header ikonu (52x52)
    logos["header"] = logos["hd"].resize((52, 52), Image.LANCZOS)

    # Taskbar ikonu (256x256 HD)
    logos["icon"] = logos["hd"].resize((256, 256), Image.LANCZOS)

    # Küçük ikon (32x32 — fallback)
    logos["small"] = logos["hd"].resize((32, 32), Image.LANCZOS)

    return logos


# ═══════════════════════════════════════════════════════════════
# RENK PALETİ
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_card": "#12121a",
    "bg_card_alt": "#1a1a2e",
    "accent": "#39ff14",
    "accent_hover": "#32e610",
    "accent_blue": "#0a1628",
    "accent_blue_light": "#1a3a5c",
    "success": "#00e676",
    "warning": "#ffab00",
    "error": "#ff5252",
    "text": "#e0e0e0",
    "text_dim": "#888899",
    "border": "#1a3a2e",
    "boost_low": "#4fc3f7",
    "boost_mid": "#ffab00",
    "boost_max": "#ff5252",
    "btn_primary": "#0d7a3e",
    "btn_primary_hover": "#0fa34e",
    "btn_secondary": "#1a2a3a",
    "btn_secondary_hover": "#2a3a4a",
    "btn_danger": "#8b0000",
    "btn_danger_hover": "#a01010",
}

SERVICES_BY_LEVEL = {
    "low": ["SysMain", "DiagTrack"],
    "medium": ["SysMain", "DiagTrack", "WSearch", "TabletInputService",
               "Fax", "PrintNotify", "MapsBroker", "lfsvc"],
    "max": ["SysMain", "DiagTrack", "WSearch", "TabletInputService",
            "Fax", "PrintNotify", "MapsBroker", "lfsvc", "Spooler",
            "WbioSrvc", "RetailDemo", "wisvc", "icssvc", "wuauserv",
            "WMPNetworkSvc", "XblAuthManager", "XblGameSave",
            "XboxGipSvc", "XboxNetApiSvc"],
}

BLOATWARE_BY_LEVEL = {
    "low": ["OneDrive.exe", "YourPhone.exe", "GameBarPresenceWriter.exe"],
    "medium": ["OneDrive.exe", "YourPhone.exe", "GameBarPresenceWriter.exe",
               "GameBar.exe", "SearchApp.exe", "SearchUI.exe", "Cortana.exe",
               "SkypeApp.exe", "SkypeBackgroundHost.exe", "HxTsr.exe",
               "HxCalendarAppImm.exe", "Microsoft.Photos.exe"],
    "max": ["OneDrive.exe", "YourPhone.exe", "GameBarPresenceWriter.exe",
            "GameBar.exe", "SearchApp.exe", "SearchUI.exe", "Cortana.exe",
            "SkypeApp.exe", "SkypeBackgroundHost.exe", "HxTsr.exe",
            "HxCalendarAppImm.exe", "Microsoft.Photos.exe", "Video.UI.exe",
            "PhoneExperienceHost.exe", "TextInputHost.exe",
            "MicrosoftEdgeUpdate.exe", "msedge.exe",
            "SecurityHealthSystray.exe", "TabTip.exe",
            "PeopleApp.exe", "CalculatorApp.exe"],
}


# ═══════════════════════════════════════════════════════════════
# 11 DİL DESTEĞİ
# ═══════════════════════════════════════════════════════════════

LANGUAGES = {
    "Türkçe": {
        "code": "tr",
        "app_title": "qBooster — Oyun Hızlandırıcı",
        "game_select": "🎯  OYUN SEÇİMİ",
        "browse": "📁 Gözat",
        "browse_placeholder": "Oyun .exe dosyasını seçin...",
        "browse_dialog_title": "Oyun .exe Dosyası Seç",
        "boost_level": "⚡  BOOST SEVİYESİ",
        "low_title": "💚 Düşük Boost",
        "low_desc": "CPU öncelik • RAM temizleme • Güç planı\nTahmini: +5~10 FPS",
        "mid_title": "💛 Orta Boost",
        "mid_desc": "Düşük + Timer res. • Nagle kapalı • Servisler\nTahmini: +10~18 FPS",
        "max_title": "❤️ Maksimum Boost",
        "max_desc": "Tüm optimizasyonlar + Realtime + Agresif temizlik\nTahmini: +15~25 FPS",
        "boost_btn": "⚡  BOOST UYGULA",
        "restore_btn": "↩  GERİ AL",
        "dns_btn": "🌐 DNS Temizle",
        "junk_btn": "🗑️ Gereksiz Dosyaları Sil",
        "ultimate_btn": "⚡ Nihai Performans",
        "ultimate_success": "[LOG] Nihai Performans Modu Başarıyla Aktif Edildi!",
        "ultimate_error": "[HATA] Mod aktif edilemedi, lütfen yönetici olarak çalıştırın!",
        "monitor": "📊  SİSTEM MONİTÖRÜ",
        "log_title": "📋  İŞLEM LOGU",
        "status_idle": "⏸  Boost uygulanmadı",
        "status_active": "🟢  {level} BOOST AKTİF",
        "status_partial": "🟡  Kısmen uygulandı — logu kontrol edin",
        "boosting": "⏳ Uygulanıyor...",
        "restoring": "⏳ Geri alınıyor...",
        "no_game": "Lütfen önce geçerli bir .exe dosyası seçin!",
        "no_game_title": "Oyun Seçilmedi",
        "boost_exists": "Zaten aktif bir boost var.\nÖnce geri alınıp yeniden uygulanacak.\nDevam edilsin mi?",
        "boost_exists_title": "Boost Aktif",
        "no_restore": "Geri yüklenecek aktif bir boost yok.",
        "close_confirm": "Boost hâlâ aktif.\nKapatmadan önce geri yüklensin mi?",
        "close_title": "Boost Aktif",
        "game_selected": "Oyun seçildi: {name}",
        "started": "qBooster {ver} başlatıldı",
        "summary": "Özet: RAM {ram}MB serbest | {svc} servis durduruldu | {proc} süreç kapatıldı",
        "level_low": "DÜŞÜK", "level_mid": "ORTA", "level_max": "MAKSİMUM",
        "language": "🌐 Dil",
        "tools": "🛠️  ARAÇLAR",
        "dns_success": "DNS önbelleği temizlendi",
        "dns_fail": "DNS temizleme başarısız: {err}",
        "junk_success": "Gereksiz dosyalar temizlendi → {count} dosya, {size}MB",
        "junk_fail": "Dosya temizleme hatası: {err}",
        "junk_confirm": "Geçici dosyalar ve önbellekler silinecek.\nDevam edilsin mi?",
        "junk_confirm_title": "Dosya Temizleme",
        "ram_cleaned": "RAM temizlendi → {amount}MB serbest bırakıldı",
    },
    "English": {
        "code": "en",
        "app_title": "qBooster — Game Optimizer",
        "game_select": "🎯  GAME SELECTION",
        "browse": "📁 Browse",
        "browse_placeholder": "Select game .exe file...",
        "browse_dialog_title": "Select Game .exe File",
        "boost_level": "⚡  BOOST LEVEL",
        "low_title": "💚 Low Boost",
        "low_desc": "CPU priority • RAM cleanup • Power plan\nEstimated: +5~10 FPS",
        "mid_title": "💛 Medium Boost",
        "mid_desc": "Low + Timer res. • Nagle off • Services\nEstimated: +10~18 FPS",
        "max_title": "❤️ Maximum Boost",
        "max_desc": "All optimizations + Realtime + Aggressive cleanup\nEstimated: +15~25 FPS",
        "boost_btn": "⚡  APPLY BOOST",
        "restore_btn": "↩  RESTORE",
        "dns_btn": "🌐 Flush DNS",
        "junk_btn": "🗑️ Clean Junk Files",
        "ultimate_btn": "⚡ Ultimate Performance",
        "ultimate_success": "[LOG] Ultimate Performance Mode Successfully Activated!",
        "ultimate_error": "[ERROR] Mode could not be activated, please run as administrator!",
        "monitor": "📊  SYSTEM MONITOR",
        "log_title": "📋  ACTION LOG",
        "status_idle": "⏸  No boost applied",
        "status_active": "🟢  {level} BOOST ACTIVE",
        "status_partial": "🟡  Partially applied — check log",
        "boosting": "⏳ Applying...",
        "restoring": "⏳ Restoring...",
        "no_game": "Please select a valid .exe file first!",
        "no_game_title": "No Game Selected",
        "boost_exists": "A boost is already active.\nIt will be restored and reapplied.\nContinue?",
        "boost_exists_title": "Boost Active",
        "no_restore": "No active boost to restore.",
        "close_confirm": "Boost is still active.\nRestore before closing?",
        "close_title": "Boost Active",
        "game_selected": "Game selected: {name}",
        "started": "qBooster {ver} started",
        "summary": "Summary: RAM {ram}MB freed | {svc} services stopped | {proc} processes killed",
        "level_low": "LOW", "level_mid": "MEDIUM", "level_max": "MAXIMUM",
        "language": "🌐 Language",
        "tools": "🛠️  TOOLS",
        "dns_success": "DNS cache flushed",
        "dns_fail": "DNS flush failed: {err}",
        "junk_success": "Junk files cleaned → {count} files, {size}MB",
        "junk_fail": "File cleanup error: {err}",
        "junk_confirm": "Temporary files and caches will be deleted.\nContinue?",
        "junk_confirm_title": "File Cleanup",
        "ram_cleaned": "RAM cleaned → {amount}MB freed",
    },
    "Deutsch": {
        "code": "de", "app_title": "qBooster — Spiel-Optimierer",
        "game_select": "🎯  SPIELAUSWAHL", "browse": "📁 Durchsuchen",
        "browse_placeholder": "Spiel-.exe-Datei auswählen...",
        "browse_dialog_title": "Spiel-.exe-Datei auswählen",
        "boost_level": "⚡  BOOST-STUFE",
        "low_title": "💚 Niedriger Boost",
        "low_desc": "CPU-Priorität • RAM • Energieplan\nGeschätzt: +5~10 FPS",
        "mid_title": "💛 Mittlerer Boost",
        "mid_desc": "Niedrig + Timer • Nagle aus • Dienste\nGeschätzt: +10~18 FPS",
        "max_title": "❤️ Maximaler Boost",
        "max_desc": "Alle Optimierungen + Echtzeit\nGeschätzt: +15~25 FPS",
        "boost_btn": "⚡  BOOST ANWENDEN", "restore_btn": "↩  WIEDERHERSTELLEN",
        "dns_btn": "🌐 DNS leeren", "junk_btn": "🗑️ Junk löschen",
        "ultimate_btn": "⚡ Ultimative Leistung",
        "ultimate_success": "[LOG] Ultimativer Leistungsmodus erfolgreich aktiviert!",
        "ultimate_error": "[FEHLER] Modus konnte nicht aktiviert werden, bitte als Administrator ausführen!",
        "monitor": "📊  SYSTEMMONITOR", "log_title": "📋  PROTOKOLL",
        "status_idle": "⏸  Kein Boost", "status_active": "🟢  {level} BOOST AKTIV",
        "status_partial": "🟡  Teilweise", "boosting": "⏳ Wird angewendet...",
        "restoring": "⏳ Wiederherstellung...",
        "no_game": "Bitte .exe-Datei wählen!", "no_game_title": "Kein Spiel",
        "boost_exists": "Boost aktiv. Fortfahren?", "boost_exists_title": "Boost aktiv",
        "no_restore": "Kein Boost.", "close_confirm": "Boost aktiv. Wiederherstellen?",
        "close_title": "Boost", "game_selected": "Spiel: {name}",
        "started": "qBooster {ver} gestartet",
        "summary": "RAM {ram}MB | {svc} Dienste | {proc} Prozesse",
        "level_low": "NIEDRIG", "level_mid": "MITTEL", "level_max": "MAXIMAL",
        "language": "🌐 Sprache", "tools": "🛠️  WERKZEUGE",
        "dns_success": "DNS geleert", "dns_fail": "DNS Fehler: {err}",
        "junk_success": "{count} Dateien, {size}MB", "junk_fail": "Fehler: {err}",
        "junk_confirm": "Temporäre Dateien löschen?", "junk_confirm_title": "Bereinigung",
        "ram_cleaned": "RAM: {amount}MB frei",
    },
    "العربية": {
        "code": "ar", "app_title": "qBooster — مُحسِّن الألعاب",
        "game_select": "🎯  اختيار اللعبة", "browse": "📁 استعراض",
        "browse_placeholder": "اختر ملف .exe...", "browse_dialog_title": "اختر .exe",
        "boost_level": "⚡  مستوى التعزيز",
        "low_title": "💚 تعزيز منخفض", "low_desc": "المعالج • الذاكرة • الطاقة\n+5~10 إطار",
        "mid_title": "💛 تعزيز متوسط", "mid_desc": "منخفض + مؤقت • Nagle\n+10~18 إطار",
        "max_title": "❤️ تعزيز أقصى", "max_desc": "جميع التحسينات\n+15~25 إطار",
        "boost_btn": "⚡  تطبيق", "restore_btn": "↩  استعادة",
        "dns_btn": "🌐 مسح DNS", "junk_btn": "🗑️ حذف الملفات",
        "ultimate_btn": "⚡ الأداء النهائي",
        "ultimate_success": "[سجل] تم تفعيل وضع الأداء النهائي بنجاح!",
        "ultimate_error": "[خطأ] تعذر تفعيل الوضع، يرجى التشغيل كمسؤول!",
        "monitor": "📊  المراقب", "log_title": "📋  السجل",
        "status_idle": "⏸  لم يتم التعزيز", "status_active": "🟢  {level} نشط",
        "status_partial": "🟡  جزئياً", "boosting": "⏳ جاري...",
        "restoring": "⏳ استعادة...", "no_game": "اختر ملف .exe!",
        "no_game_title": "لا لعبة", "boost_exists": "تعزيز موجود. متابعة؟",
        "boost_exists_title": "نشط", "no_restore": "لا يوجد تعزيز.",
        "close_confirm": "استعادة قبل الإغلاق؟", "close_title": "نشط",
        "game_selected": "اللعبة: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} خدمة | {proc} عملية",
        "level_low": "منخفض", "level_mid": "متوسط", "level_max": "أقصى",
        "language": "🌐 اللغة", "tools": "🛠️  الأدوات",
        "dns_success": "تم مسح DNS", "dns_fail": "فشل: {err}",
        "junk_success": "{count} ملف، {size}MB", "junk_fail": "خطأ: {err}",
        "junk_confirm": "حذف الملفات المؤقتة؟", "junk_confirm_title": "تنظيف",
        "ram_cleaned": "الذاكرة: {amount}MB",
    },
    "中文": {
        "code": "zh", "app_title": "qBooster — 游戏加速器",
        "game_select": "🎯  选择游戏", "browse": "📁 浏览",
        "browse_placeholder": "选择 .exe 文件...", "browse_dialog_title": "选择 .exe",
        "boost_level": "⚡  加速等级",
        "low_title": "💚 低级", "low_desc": "CPU • 内存 • 电源\n+5~10 FPS",
        "mid_title": "💛 中级", "mid_desc": "低级 + 定时器 • Nagle\n+10~18 FPS",
        "max_title": "❤️ 最大", "max_desc": "全部优化 + 实时\n+15~25 FPS",
        "boost_btn": "⚡  应用加速", "restore_btn": "↩  恢复",
        "dns_btn": "🌐 清除DNS", "junk_btn": "🗑️ 清理垃圾",
        "ultimate_btn": "⚡ 终极性能",
        "ultimate_success": "[日志] 终极性能模式已成功激活！",
        "ultimate_error": "[错误] 无法激活模式，请以管理员身份运行！",
        "monitor": "📊  系统监控", "log_title": "📋  日志",
        "status_idle": "⏸  未加速", "status_active": "🟢  {level} 已激活",
        "status_partial": "🟡  部分", "boosting": "⏳ 应用中...",
        "restoring": "⏳ 恢复中...", "no_game": "请选择 .exe！",
        "no_game_title": "未选择", "boost_exists": "已有加速。继续？",
        "boost_exists_title": "已激活", "no_restore": "无加速。",
        "close_confirm": "关闭前恢复？", "close_title": "已激活",
        "game_selected": "游戏: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} 服务 | {proc} 进程",
        "level_low": "低", "level_mid": "中", "level_max": "最大",
        "language": "🌐 语言", "tools": "🛠️  工具",
        "dns_success": "DNS已清除", "dns_fail": "失败: {err}",
        "junk_success": "{count} 文件, {size}MB", "junk_fail": "错误: {err}",
        "junk_confirm": "删除临时文件？", "junk_confirm_title": "清理",
        "ram_cleaned": "内存: {amount}MB",
    },
    "日本語": {
        "code": "ja", "app_title": "qBooster — ゲームブースター",
        "game_select": "🎯  ゲーム選択", "browse": "📁 参照",
        "browse_placeholder": ".exeファイルを選択...", "browse_dialog_title": ".exe選択",
        "boost_level": "⚡  ブーストレベル",
        "low_title": "💚 低", "low_desc": "CPU • RAM • 電源\n+5~10 FPS",
        "mid_title": "💛 中", "mid_desc": "低 + タイマー • Nagle\n+10~18 FPS",
        "max_title": "❤️ 最大", "max_desc": "全最適化 + リアルタイム\n+15~25 FPS",
        "boost_btn": "⚡  ブースト適用", "restore_btn": "↩  復元",
        "dns_btn": "🌐 DNSクリア", "junk_btn": "🗑️ ジャンク削除",
        "ultimate_btn": "⚡ 究極性能",
        "ultimate_success": "[ログ] 究極性能モードが正常に有効化されました！",
        "ultimate_error": "[エラー] モードを有効化できませんでした。管理者として実行してください！",
        "monitor": "📊  モニター", "log_title": "📋  ログ",
        "status_idle": "⏸  未適用", "status_active": "🟢  {level} アクティブ",
        "status_partial": "🟡  部分", "boosting": "⏳ 適用中...",
        "restoring": "⏳ 復元中...", "no_game": ".exeを選択！",
        "no_game_title": "未選択", "boost_exists": "ブースト有。続行？",
        "boost_exists_title": "アクティブ", "no_restore": "ブーストなし。",
        "close_confirm": "復元して閉じる？", "close_title": "アクティブ",
        "game_selected": "ゲーム: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc}サービス | {proc}プロセス",
        "level_low": "低", "level_mid": "中", "level_max": "最大",
        "language": "🌐 言語", "tools": "🛠️  ツール",
        "dns_success": "DNSクリア完了", "dns_fail": "失敗: {err}",
        "junk_success": "{count}ファイル, {size}MB", "junk_fail": "エラー: {err}",
        "junk_confirm": "一時ファイル削除？", "junk_confirm_title": "クリーン",
        "ram_cleaned": "RAM: {amount}MB",
    },
    "Español": {
        "code": "es", "app_title": "qBooster — Optimizador",
        "game_select": "🎯  SELECCIÓN", "browse": "📁 Explorar",
        "browse_placeholder": "Seleccione .exe...", "browse_dialog_title": "Seleccionar .exe",
        "boost_level": "⚡  NIVEL",
        "low_title": "💚 Bajo", "low_desc": "CPU • RAM • Energía\n+5~10 FPS",
        "mid_title": "💛 Medio", "mid_desc": "Bajo + Timer • Nagle\n+10~18 FPS",
        "max_title": "❤️ Máximo", "max_desc": "Todo + Tiempo real\n+15~25 FPS",
        "boost_btn": "⚡  APLICAR", "restore_btn": "↩  RESTAURAR",
        "dns_btn": "🌐 Limpiar DNS", "junk_btn": "🗑️ Limpiar basura",
        "ultimate_btn": "⚡ Rendimiento Máximo",
        "ultimate_success": "[LOG] ¡Modo de Rendimiento Máximo activado exitosamente!",
        "ultimate_error": "[ERROR] No se pudo activar el modo, ¡ejecute como administrador!",
        "monitor": "📊  MONITOR", "log_title": "📋  REGISTRO",
        "status_idle": "⏸  Sin boost", "status_active": "🟢  {level} ACTIVO",
        "status_partial": "🟡  Parcial", "boosting": "⏳ Aplicando...",
        "restoring": "⏳ Restaurando...", "no_game": "¡Seleccione .exe!",
        "no_game_title": "Sin juego", "boost_exists": "Boost activo. ¿Continuar?",
        "boost_exists_title": "Activo", "no_restore": "Sin boost.",
        "close_confirm": "¿Restaurar?", "close_title": "Activo",
        "game_selected": "Juego: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} servicios | {proc} procesos",
        "level_low": "BAJO", "level_mid": "MEDIO", "level_max": "MÁXIMO",
        "language": "🌐 Idioma", "tools": "🛠️  HERRAMIENTAS",
        "dns_success": "DNS limpiada", "dns_fail": "Error: {err}",
        "junk_success": "{count} archivos, {size}MB", "junk_fail": "Error: {err}",
        "junk_confirm": "¿Eliminar temporales?", "junk_confirm_title": "Limpieza",
        "ram_cleaned": "RAM: {amount}MB",
    },
    "Français": {
        "code": "fr", "app_title": "qBooster — Optimiseur",
        "game_select": "🎯  SÉLECTION", "browse": "📁 Parcourir",
        "browse_placeholder": "Sélectionnez .exe...", "browse_dialog_title": "Sélectionner .exe",
        "boost_level": "⚡  NIVEAU",
        "low_title": "💚 Faible", "low_desc": "CPU • RAM • Énergie\n+5~10 FPS",
        "mid_title": "💛 Moyen", "mid_desc": "Faible + Timer • Nagle\n+10~18 FPS",
        "max_title": "❤️ Maximum", "max_desc": "Tout + Temps réel\n+15~25 FPS",
        "boost_btn": "⚡  APPLIQUER", "restore_btn": "↩  RESTAURER",
        "dns_btn": "🌐 Vider DNS", "junk_btn": "🗑️ Nettoyer",
        "ultimate_btn": "⚡ Performance Ultime",
        "ultimate_success": "[LOG] Mode Performance Ultime activé avec succès!",
        "ultimate_error": "[ERREUR] Impossible d'activer le mode, veuillez exécuter en tant qu'administrateur!",
        "monitor": "📊  MONITEUR", "log_title": "📋  JOURNAL",
        "status_idle": "⏸  Aucun boost", "status_active": "🟢  {level} ACTIF",
        "status_partial": "🟡  Partiel", "boosting": "⏳ Application...",
        "restoring": "⏳ Restauration...", "no_game": "Sélectionnez .exe!",
        "no_game_title": "Aucun jeu", "boost_exists": "Boost actif. Continuer?",
        "boost_exists_title": "Actif", "no_restore": "Aucun boost.",
        "close_confirm": "Restaurer?", "close_title": "Actif",
        "game_selected": "Jeu: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} services | {proc} processus",
        "level_low": "FAIBLE", "level_mid": "MOYEN", "level_max": "MAXIMUM",
        "language": "🌐 Langue", "tools": "🛠️  OUTILS",
        "dns_success": "DNS vidé", "dns_fail": "Erreur: {err}",
        "junk_success": "{count} fichiers, {size}MB", "junk_fail": "Erreur: {err}",
        "junk_confirm": "Supprimer temporaires?", "junk_confirm_title": "Nettoyage",
        "ram_cleaned": "RAM: {amount}MB",
    },
    "Русский": {
        "code": "ru", "app_title": "qBooster — Оптимизатор",
        "game_select": "🎯  ВЫБОР ИГРЫ", "browse": "📁 Обзор",
        "browse_placeholder": "Выберите .exe...", "browse_dialog_title": "Выбрать .exe",
        "boost_level": "⚡  УРОВЕНЬ",
        "low_title": "💚 Низкий", "low_desc": "CPU • RAM • Питание\n+5~10 FPS",
        "mid_title": "💛 Средний", "mid_desc": "Низкий + Таймер • Nagle\n+10~18 FPS",
        "max_title": "❤️ Максимум", "max_desc": "Все + Реальное время\n+15~25 FPS",
        "boost_btn": "⚡  ПРИМЕНИТЬ", "restore_btn": "↩  ВОССТАНОВИТЬ",
        "dns_btn": "🌐 Очистить DNS", "junk_btn": "🗑️ Удалить мусор",
        "ultimate_btn": "⚡ Максимальная Производительность",
        "ultimate_success": "[ЛОГ] Режим Максимальной Производительности успешно активирован!",
        "ultimate_error": "[ОШИБКА] Не удалось активировать режим, запустите от имени администратора!",
        "monitor": "📊  МОНИТОР", "log_title": "📋  ЖУРНАЛ",
        "status_idle": "⏸  Нет буста", "status_active": "🟢  {level} АКТИВЕН",
        "status_partial": "🟡  Частично", "boosting": "⏳ Применение...",
        "restoring": "⏳ Восстановление...", "no_game": "Выберите .exe!",
        "no_game_title": "Нет игры", "boost_exists": "Буст активен. Продолжить?",
        "boost_exists_title": "Активен", "no_restore": "Нет буста.",
        "close_confirm": "Восстановить?", "close_title": "Активен",
        "game_selected": "Игра: {name}", "started": "qBooster {ver}",
        "summary": "{ram}МБ | {svc} служб | {proc} процессов",
        "level_low": "НИЗКИЙ", "level_mid": "СРЕДНИЙ", "level_max": "МАКСИМУМ",
        "language": "🌐 Язык", "tools": "🛠️  ИНСТРУМЕНТЫ",
        "dns_success": "DNS очищен", "dns_fail": "Ошибка: {err}",
        "junk_success": "{count} файлов, {size}МБ", "junk_fail": "Ошибка: {err}",
        "junk_confirm": "Удалить временные?", "junk_confirm_title": "Очистка",
        "ram_cleaned": "RAM: {amount}МБ",
    },
    "Afrikaans": {
        "code": "af", "app_title": "qBooster — Optimeerder",
        "game_select": "🎯  KEUSE", "browse": "📁 Blaai",
        "browse_placeholder": "Kies .exe...", "browse_dialog_title": "Kies .exe",
        "boost_level": "⚡  VLAK",
        "low_title": "💚 Laag", "low_desc": "CPU • RAM • Krag\n+5~10 FPS",
        "mid_title": "💛 Medium", "mid_desc": "Laag + Tydhouer\n+10~18 FPS",
        "max_title": "❤️ Maksimum", "max_desc": "Alles + Intydse\n+15~25 FPS",
        "boost_btn": "⚡  TOEPAS", "restore_btn": "↩  HERSTEL",
        "dns_btn": "🌐 DNS skoonmaak", "junk_btn": "🗑️ Rommel verwyder",
        "ultimate_btn": "⚡ Uiterste Prestasie",
        "ultimate_success": "[LOG] Uiterste Prestasie Modus suksesvol geaktiveer!",
        "ultimate_error": "[FOUT] Kon nie modus aktiveer nie, voer asseblief as administrateur uit!",
        "monitor": "📊  MONITOR", "log_title": "📋  LOG",
        "status_idle": "⏸  Geen boost", "status_active": "🟢  {level} AKTIEF",
        "status_partial": "🟡  Gedeeltelik", "boosting": "⏳ Toepas...",
        "restoring": "⏳ Herstel...", "no_game": "Kies .exe!",
        "no_game_title": "Geen speletjie", "boost_exists": "Boost aktief. Voortgaan?",
        "boost_exists_title": "Aktief", "no_restore": "Geen boost.",
        "close_confirm": "Herstel?", "close_title": "Aktief",
        "game_selected": "Speletjie: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} dienste | {proc} prosesse",
        "level_low": "LAAG", "level_mid": "MEDIUM", "level_max": "MAKSIMUM",
        "language": "🌐 Taal", "tools": "🛠️  GEREEDSKAP",
        "dns_success": "DNS skoongemaak", "dns_fail": "Fout: {err}",
        "junk_success": "{count} lêers, {size}MB", "junk_fail": "Fout: {err}",
        "junk_confirm": "Tydelike lêers verwyder?", "junk_confirm_title": "Skoonmaak",
        "ram_cleaned": "RAM: {amount}MB",
    },
    "فارسی": {
        "code": "fa", "app_title": "qBooster — بهینه‌ساز",
        "game_select": "🎯  انتخاب بازی", "browse": "📁 مرور",
        "browse_placeholder": "فایل .exe را انتخاب کنید...", "browse_dialog_title": "انتخاب .exe",
        "boost_level": "⚡  سطح تقویت",
        "low_title": "💚 کم", "low_desc": "CPU • RAM • برق\n+5~10 FPS",
        "mid_title": "💛 متوسط", "mid_desc": "کم + تایمر • Nagle\n+10~18 FPS",
        "max_title": "❤️ حداکثر", "max_desc": "همه + زمان واقعی\n+15~25 FPS",
        "boost_btn": "⚡  اعمال", "restore_btn": "↩  بازگردانی",
        "dns_btn": "🌐 پاکسازی DNS", "junk_btn": "🗑️ حذف فایل‌ها",
        "ultimate_btn": "⚡ عملکرد نهایی",
        "ultimate_success": "[لاگ] حالت عملکرد نهایی با موفقیت فعال شد!",
        "ultimate_error": "[خطا] حالت فعال نشد، لطفاً به عنوان مدیر اجرا کنید!",
        "monitor": "📊  مانیتور", "log_title": "📋  گزارش",
        "status_idle": "⏸  بدون تقویت", "status_active": "🟢  {level} فعال",
        "status_partial": "🟡  بخشی", "boosting": "⏳ اعمال...",
        "restoring": "⏳ بازگردانی...", "no_game": "فایل .exe انتخاب کنید!",
        "no_game_title": "بدون بازی", "boost_exists": "تقویت فعال. ادامه؟",
        "boost_exists_title": "فعال", "no_restore": "بدون تقویت.",
        "close_confirm": "بازگردانی؟", "close_title": "فعال",
        "game_selected": "بازی: {name}", "started": "qBooster {ver}",
        "summary": "{ram}MB | {svc} سرویس | {proc} فرآیند",
        "level_low": "کم", "level_mid": "متوسط", "level_max": "حداکثر",
        "language": "🌐 زبان", "tools": "🛠️  ابزارها",
        "dns_success": "DNS پاک شد", "dns_fail": "خطا: {err}",
        "junk_success": "{count} فایل، {size}MB", "junk_fail": "خطا: {err}",
        "junk_confirm": "حذف فایل‌های موقت؟", "junk_confirm_title": "پاکسازی",
        "ram_cleaned": "RAM: {amount}MB",
    },
}


# ═══════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            f'"{os.path.abspath(sys.argv[0])}"', None, 1)
        sys.exit(0)
    except: pass

def ensure_config_dir(): os.makedirs(CONFIG_DIR, exist_ok=True)

def log_action(msg):
    ensure_config_dir()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{ts}] {msg}\n")

def save_restore_state(s):
    ensure_config_dir()
    with open(RESTORE_FILE, "w", encoding="utf-8") as f: json.dump(s, f, indent=2)

def load_restore_state():
    if os.path.exists(RESTORE_FILE):
        with open(RESTORE_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"language": "Türkçe"}

def save_config(c):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(c, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# WINDOWS API
# ═══════════════════════════════════════════════════════════════

TOKEN_ADJUST_PRIVILEGES = 0x0020; TOKEN_QUERY = 0x0008; SE_PRIVILEGE_ENABLED = 0x00000002

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]
class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]
class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

def enable_privilege(name):
    try:
        tok = wintypes.HANDLE()
        ctypes.windll.advapi32.OpenProcessToken(
            ctypes.windll.kernel32.GetCurrentProcess(),
            TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(tok))
        lu = LUID()
        ctypes.windll.advapi32.LookupPrivilegeValueW(None, name, ctypes.byref(lu))
        tp = TOKEN_PRIVILEGES(); tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = lu; tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        r = ctypes.windll.advapi32.AdjustTokenPrivileges(tok, False, ctypes.byref(tp), 0, None, None)
        ctypes.windll.kernel32.CloseHandle(tok); return bool(r)
    except: return False


# ═══════════════════════════════════════════════════════════════
# SİSTEM OPTİMİZATÖR (Önceki sürümle aynı — kısaltılmış)
# ═══════════════════════════════════════════════════════════════

class SystemOptimizer:
    def __init__(self):
        self.restore_state = load_restore_state()
        self.stopped_services, self.killed_processes = [], []
        self.original_power_plan = None
        self.timer_resolution_set = self.nagle_modified = False
        self.game_pid = None; self.is_boosted = False
        self._log_cbs, self._prog_cbs = [], []

    def add_log_callback(self, cb): self._log_cbs.append(cb)
    def add_progress_callback(self, cb): self._prog_cbs.append(cb)
    def _log(self, m, l="info"):
        log_action(m)
        for c in self._log_cbs: c(m, l)
    def _set_progress(self, v):
        for c in self._prog_cbs: c(v)

    def _wait_for_process_ready(self, pid, exe, timeout=60, interval=1.5):
        self._log(f"Waiting for process... (max {timeout}s)", "info")
        start = time.time(); found = None; stable = 0
        while (time.time() - start) < timeout:
            tp = self._find_pid(pid, exe)
            if tp is None: stable = 0; time.sleep(interval); continue
            r = self._check_ready(tp)
            if r["is_ready"]:
                stable += 1; found = tp
                if stable >= 3:
                    self._log(f"Process ready! PID:{found} RAM:{r['memory_mb']:.0f}MB", "success")
                    return found
            else: stable = 0
            time.sleep(interval)
        return found

    def _find_pid(self, orig, exe):
        try:
            p = psutil.Process(orig)
            if p.is_running() and p.status() != psutil.STATUS_ZOMBIE: return orig
        except: pass
        el = exe.lower(); cs = []
        for p in psutil.process_iter(["pid", "name", "create_time"]):
            try:
                if p.info["name"] and p.info["name"].lower() == el: cs.append(p.info)
            except: continue
        if cs: cs.sort(key=lambda x: x.get("create_time", 0), reverse=True); return cs[0]["pid"]
        stem = exe.rsplit(".", 1)[0].lower()
        for p in psutil.process_iter(["pid", "name", "create_time"]):
            try:
                n = p.info["name"]
                if n and stem in n.lower() and n.lower() != el: cs.append(p.info)
            except: continue
        if cs: cs.sort(key=lambda x: x.get("create_time", 0), reverse=True); return cs[0]["pid"]
        return None

    def _check_ready(self, pid):
        r = {"is_ready": False, "status": "?", "memory_mb": 0, "cpu_percent": 0, "threads": 0}
        try:
            p = psutil.Process(pid); s = p.status(); r["status"] = s
            if s in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD): return r
            m = p.memory_info().rss / (1024*1024); r["memory_mb"] = m
            if m < 50: return r
            r["cpu_percent"] = p.cpu_percent(interval=0.5)
            r["threads"] = p.num_threads()
            if m >= 50 and r["threads"] >= 2: r["is_ready"] = True
        except: pass
        return r

    def _apply_proc_opts(self, pid, level):
        ok = 0
        try:
            if self.set_priority(pid, level): ok += 1
        except: pass
        try:
            if self.set_affinity(pid, level): ok += 1
        except: pass
        try:
            if self.set_io(pid): ok += 1
        except: pass
        self._log(f"Process opts: {ok}/3", "success" if ok == 3 else "warning")

    def set_priority(self, pid, level):
        try:
            p = psutil.Process(pid)
            if level == "max":
                enable_privilege("SeIncreaseBasePriorityPrivilege")
                p.nice(psutil.REALTIME_PRIORITY_CLASS); self._log("CPU: REALTIME", "success")
            else:
                p.nice(psutil.HIGH_PRIORITY_CLASS); self._log("CPU: HIGH", "success")
            return True
        except psutil.AccessDenied:
            try: psutil.Process(pid).nice(psutil.HIGH_PRIORITY_CLASS); return True
            except: return False
        except: return False

    def set_affinity(self, pid, level):
        try:
            p = psutil.Process(pid); cc = psutil.cpu_count(logical=True)
            if level == "max" and cc >= 8:
                n = min(cc // 2 + 2, cc); p.cpu_affinity(list(range(n)))
            else: p.cpu_affinity(list(range(cc)))
            return True
        except: return False

    def lower_bg(self):
        skip = {"System","smss.exe","csrss.exe","wininit.exe","services.exe","lsass.exe",
                "svchost.exe","dwm.exe","explorer.exe","winlogon.exe","fontdrvhost.exe",
                "conhost.exe","python.exe","pythonw.exe","RuntimeBroker.exe","sihost.exe","taskhostw.exe"}
        c = 0
        for p in psutil.process_iter(["pid", "name"]):
            try:
                n = p.info["name"]
                if n and n not in skip and p.info["pid"] != self.game_pid:
                    pp = psutil.Process(p.info["pid"])
                    if pp.nice() == psutil.NORMAL_PRIORITY_CLASS: pp.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS); c += 1
            except: continue
        if c: self._log(f"{c} bg processes lowered", "success")

    def clean_ws(self):
        b = psutil.virtual_memory().available
        for p in psutil.process_iter(["pid"]):
            try:
                h = ctypes.windll.kernel32.OpenProcess(0x0500, False, p.info["pid"])
                if h: ctypes.windll.kernel32.SetProcessWorkingSetSizeEx(h, ctypes.c_size_t(-1), ctypes.c_size_t(-1), 0); ctypes.windll.kernel32.CloseHandle(h)
            except: continue
        f = max(0, (psutil.virtual_memory().available - b) / (1024*1024))
        self._log(f"WS cleaned → {f:.0f}MB", "success"); return f

    def clean_standby(self):
        b = psutil.virtual_memory().available
        try:
            enable_privilege("SeProfileSingleProcessPrivilege"); enable_privilege("SeIncreaseQuotaPrivilege")
            cmd = ctypes.c_ulong(4); ctypes.WinDLL("ntdll").NtSetSystemInformation(0x50, ctypes.byref(cmd), ctypes.sizeof(cmd))
            f = max(0, (psutil.virtual_memory().available - b) / (1024*1024))
            self._log(f"Standby cleaned → {f:.0f}MB", "success"); return f
        except: return 0

    def optimize_ram(self, level):
        t = self.clean_ws()
        if level in ("medium", "max"): t += self.clean_standby()
        if level == "max": time.sleep(0.5); t += self.clean_ws()
        return t

    def flush_dns(self):
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=0x08000000)
            subprocess.run(["netsh", "winsock", "reset", "catalog"], capture_output=True, creationflags=0x08000000)
            subprocess.run(["net", "stop", "dnscache"], capture_output=True, creationflags=0x08000000)
            subprocess.run(["net", "start", "dnscache"], capture_output=True, creationflags=0x08000000)
            subprocess.run(["netsh", "interface", "ip", "delete", "arpcache"], capture_output=True, creationflags=0x08000000)
            self._log("DNS flushed", "success"); return True
        except Exception as e: self._log(f"DNS fail: {e}", "error"); return False

    def clean_junk(self):
        result = {"count": 0, "size_mb": 0.0}
        dirs = [os.environ.get("TEMP",""), os.environ.get("TMP",""),
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp"),
                os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Temp"),
                os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Prefetch")]
        la = os.environ.get("LOCALAPPDATA", "")
        if la:
            dirs += [os.path.join(la, "Google", "Chrome", "User Data", "Default", "Cache"),
                     os.path.join(la, "Microsoft", "Edge", "User Data", "Default", "Cache")]
        exts = {".tmp",".temp",".log",".old",".bak",".dmp",".etl",".cache",".chk"}
        for d in dirs:
            if not d or not os.path.isdir(d): continue
            for root, dd, ff in os.walk(d, topdown=False):
                for fn in ff:
                    fp = os.path.join(root, fn)
                    try:
                        ext = os.path.splitext(fn)[1].lower()
                        if any(t in root for t in ["Temp","temp","Cache","Prefetch"]) or ext in exts:
                            sz = os.path.getsize(fp); os.remove(fp)
                            result["count"] += 1; result["size_mb"] += sz / (1024*1024)
                    except: continue
                for dn in dd:
                    try:
                        dp = os.path.join(root, dn)
                        if not os.listdir(dp): os.rmdir(dp)
                    except: continue
        self._log(f"Junk: {result['count']} files, {result['size_mb']:.1f}MB", "success")
        return result

    def get_power(self):
        try:
            r = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True, creationflags=0x08000000, encoding='utf-8', errors='ignore')
            if r.returncode == 0 and r.stdout:
                for p in r.stdout.strip().split():
                    if len(p) == 36 and p.count("-") == 4: return p
        except: pass
        return None

    def set_power(self, level):
        try:
            self.original_power_plan = self.get_power()
            if level == "max":
                g = "e9a42b02-d5df-448d-aa00-03f14749eb61"
                subprocess.run(["powercfg", "-duplicatescheme", g], capture_output=True, creationflags=0x08000000)
                if subprocess.run(["powercfg", "/setactive", g], capture_output=True, creationflags=0x08000000).returncode == 0:
                    self._log("Power: Ultimate", "success"); return True
                level = "medium"
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, creationflags=0x08000000)
            self._log("Power: High", "success"); return True
        except: return False

    def activate_ultimate_performance(self):
        """
        Nihai Performans (Ultimate Performance) modunu aktif eder.
        Returns: True başarılı, False hata
        """
        try:
            # Mevcut güç planını kaydet
            if not self.original_power_plan:
                self.original_power_plan = self.get_power()
            
            self._log("🔍 Mevcut güç planı kontrol ediliyor...", "info")
            
            # ══════════════════════════════════════
            # STRATEJİ 1: Mevcut Ultimate Performance'ı bul
            # ══════════════════════════════════════
            ultimate_guid = None
            list_result = subprocess.run(
                ["powercfg", "/list"],
                capture_output=True,
                text=True,
                creationflags=0x08000000,
                encoding='utf-8',
                errors='ignore'
            )
            
            if list_result.returncode == 0 and list_result.stdout:
                import re
                keywords = ["ultimate", "nihai", "ultime", "ultimative", "máximo", "最大", "최고"]
                
                for line in list_result.stdout.split('\n'):
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in keywords):
                        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', 
                                        line, re.IGNORECASE)
                        if match:
                            ultimate_guid = match.group(1)
                            self._log(f"✅ Mevcut Ultimate Performance bulundu: {ultimate_guid}", "success")
                            break
            
            # ══════════════════════════════════════
            # STRATEJİ 2: Yoksa High Performance + Optimizasyon
            # ══════════════════════════════════════
            if not ultimate_guid:
                self._log("⚙️ Ultimate Performance bulunamadı, High Performance optimize ediliyor...", "info")
                
                # High Performance GUID
                high_perf_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
                
                # High Performance'ı aktif et
                activate = subprocess.run(
                    ["powercfg", "/setactive", high_perf_guid],
                    capture_output=True,
                    text=True,
                    creationflags=0x08000000,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if activate.returncode != 0:
                    self._log("❌ High Performance aktifleştirilemedi", "error")
                    self._log("[HATA] Mod aktif edilemedi, lütfen yönetici olarak çalıştırın!", "error")
                    return False
                
                # High Performance ayarlarını maksimum performansa çek
                settings = [
                    # CPU minimum %100
                    ("/setacvalueindex", high_perf_guid, "SUB_PROCESSOR", "PROCTHROTTLEMIN", "100"),
                    ("/setdcvalueindex", high_perf_guid, "SUB_PROCESSOR", "PROCTHROTTLEMIN", "100"),
                    # CPU maksimum %100
                    ("/setacvalueindex", high_perf_guid, "SUB_PROCESSOR", "PROCTHROTTLEMAX", "100"),
                    ("/setdcvalueindex", high_perf_guid, "SUB_PROCESSOR", "PROCTHROTTLEMAX", "100"),
                    # PCI Express güç yönetimi kapalı
                    ("/setacvalueindex", high_perf_guid, "SUB_PCIEXPRESS", "ASPM", "0"),
                    ("/setdcvalueindex", high_perf_guid, "SUB_PCIEXPRESS", "ASPM", "0"),
                    # Disk kapatmayı devre dışı bırak
                    ("/setacvalueindex", high_perf_guid, "SUB_DISK", "DISKIDLE", "0"),
                    ("/setdcvalueindex", high_perf_guid, "SUB_DISK", "DISKIDLE", "0"),
                ]
                
                for setting in settings:
                    subprocess.run(
                        ["powercfg"] + list(setting),
                        capture_output=True,
                        creationflags=0x08000000
                    )
                
                # Ayarları uygula
                subprocess.run(
                    ["powercfg", "/setactive", high_perf_guid],
                    capture_output=True,
                    creationflags=0x08000000
                )
                
                self._log("✅ High Performance maksimum performansa optimize edildi", "success")
                self._log("═══════════════════════════════════", "success")
                self._log("[LOG] Nihai Performans Modu Başarıyla Aktif Edildi!", "success")
                self._log("═══════════════════════════════════", "success")
                return True
            
            # ══════════════════════════════════════
            # STRATEJİ 3: Ultimate Performance'ı aktif et
            # ══════════════════════════════════════
            self._log(f"🔄 Ultimate Performance aktifleştiriliyor...", "info")
            activate_result = subprocess.run(
                ["powercfg", "/setactive", ultimate_guid],
                capture_output=True,
                text=True,
                creationflags=0x08000000,
                encoding='utf-8',
                errors='ignore'
            )
            
            if activate_result.returncode == 0:
                # Doğrulama
                time.sleep(0.3)
                verify = subprocess.run(
                    ["powercfg", "/getactivescheme"],
                    capture_output=True,
                    text=True,
                    creationflags=0x08000000,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if verify.returncode == 0 and verify.stdout and ultimate_guid.lower() in verify.stdout.lower():
                    self._log("═══════════════════════════════════", "success")
                    self._log("[LOG] Nihai Performans Modu Başarıyla Aktif Edildi!", "success")
                    self._log("═══════════════════════════════════", "success")
                    return True
                else:
                    self._log("❌ Doğrulama başarısız", "error")
                    self._log("[HATA] Mod aktif edilemedi, lütfen yönetici olarak çalıştırın!", "error")
                    return False
            else:
                err_msg = (activate_result.stderr.strip() if activate_result.stderr else "") or \
                          (activate_result.stdout.strip() if activate_result.stdout else "Bilinmeyen hata")
                self._log(f"❌ Aktivasyon hatası: {err_msg}", "error")
                self._log("[HATA] Mod aktif edilemedi, lütfen yönetici olarak çalıştırın!", "error")
                return False
                
        except Exception as e:
            self._log(f"❌ Kritik hata: {str(e)}", "error")
            self._log("[HATA] Mod aktif edilemedi, lütfen yönetici olarak çalıştırın!", "error")
            return False

    def restore_power(self):
        if self.original_power_plan:
            try: subprocess.run(["powercfg", "/setactive", self.original_power_plan], capture_output=True, creationflags=0x08000000); return True
            except: pass
        return False

    def set_timer(self, level):
        try:
            c = ctypes.c_ulong(); d = 5000 if level == "max" else 10000
            ctypes.WinDLL("ntdll").NtSetTimerResolution(ctypes.c_ulong(d), ctypes.c_byte(1), ctypes.byref(c))
            self.timer_resolution_set = True; self._log(f"Timer: {c.value/10000:.1f}ms", "success"); return True
        except: return False

    def restore_timer(self):
        if not self.timer_resolution_set: return True
        try:
            c = ctypes.c_ulong()
            ctypes.WinDLL("ntdll").NtSetTimerResolution(ctypes.c_ulong(156250), ctypes.c_byte(0), ctypes.byref(c))
            self.timer_resolution_set = False; return True
        except: return False

    def disable_nagle(self):
        try:
            kp = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, kp); c = 0; i = 0
            while True:
                try:
                    s = winreg.EnumKey(reg, i)
                    sk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{kp}\\{s}", 0, winreg.KEY_ALL_ACCESS)
                    winreg.SetValueEx(sk, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(sk, "TCPNoDelay", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(sk, "TcpDelAckTicks", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(sk); c += 1; i += 1
                except OSError: break
            winreg.CloseKey(reg); self.nagle_modified = True; self._log(f"Nagle off → {c}", "success"); return True
        except: return False

    def restore_nagle(self):
        if not self.nagle_modified: return True
        try:
            kp = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, kp); i = 0
            while True:
                try:
                    s = winreg.EnumKey(reg, i)
                    sk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{kp}\\{s}", 0, winreg.KEY_ALL_ACCESS)
                    for v in ("TcpAckFrequency", "TCPNoDelay", "TcpDelAckTicks"):
                        try: winreg.DeleteValue(sk, v)
                        except: pass
                    winreg.CloseKey(sk); i += 1
                except OSError: break
            winreg.CloseKey(reg); self.nagle_modified = False; return True
        except: return False

    def stop_svcs(self, level):
        svcs = SERVICES_BY_LEVEL.get(level, []); c = 0
        for s in svcs:
            try:
                if "RUNNING" in subprocess.run(["sc", "query", s], capture_output=True, text=True, creationflags=0x08000000).stdout:
                    subprocess.run(["sc", "stop", s], capture_output=True, creationflags=0x08000000)
                    self.stopped_services.append(s); c += 1
            except: continue
        if c: self._log(f"{c} services stopped", "success")
        return c

    def restore_svcs(self):
        c = 0
        for s in self.stopped_services:
            try: subprocess.run(["sc", "start", s], capture_output=True, creationflags=0x08000000); c += 1
            except: continue
        self.stopped_services.clear(); return c

    def kill_bloat(self, level):
        ts = BLOATWARE_BY_LEVEL.get(level, []); c = 0
        for p in psutil.process_iter(["pid", "name"]):
            try:
                if p.info["name"] and p.info["name"] in ts: psutil.Process(p.info["pid"]).terminate(); c += 1
            except: continue
        if c: self._log(f"{c} bloatware killed", "success")
        return c

    def disable_gb(self):
        try:
            for kp, vs in [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR", [("AppCaptureEnabled", 0)]),
                           (r"SOFTWARE\Microsoft\GameBar", [("AllowAutoGameMode", 1), ("ShowStartupPanel", 0), ("UseNexusForGameBarEnabled", 0)])]:
                try: k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, kp, 0, winreg.KEY_ALL_ACCESS)
                except: k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, kp)
                for n, v in vs: winreg.SetValueEx(k, n, 0, winreg.REG_DWORD, v)
                winreg.CloseKey(k)
            return True
        except: return False

    def set_gpu(self, path):
        try:
            kp = r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences"
            try: k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, kp, 0, winreg.KEY_ALL_ACCESS)
            except: k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, kp)
            winreg.SetValueEx(k, path, 0, winreg.REG_SZ, "GpuPreference=2;"); winreg.CloseKey(k); return True
        except: return False

    def opt_visual(self, level):
        if level not in ("medium", "max"): return False
        try:
            kp = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            try: k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, kp, 0, winreg.KEY_ALL_ACCESS)
            except: k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, kp)
            winreg.SetValueEx(k, "VisualFXSetting", 0, winreg.REG_DWORD, 2 if level == "max" else 3)
            winreg.CloseKey(k); return True
        except: return False

    def set_io(self, pid):
        try:
            h = ctypes.windll.kernel32.OpenProcess(0x0600, False, pid)
            if h:
                io = ctypes.c_ulong(3)
                ctypes.windll.ntdll.NtSetInformationProcess(h, 33, ctypes.byref(io), ctypes.sizeof(io))
                ctypes.windll.kernel32.CloseHandle(h); self._log("I/O: HIGH", "success"); return True
        except: pass
        return False

    def apply_boost(self, game_path, level):
        res = {"ram_freed": 0, "services_stopped": 0, "processes_killed": 0, "success": True}
        steps = 14; n = [0]
        def step(): n[0] += 1; self._set_progress(n[0] / steps)

        self._log(f"═══ BOOST ═══ {level.upper()}", "info")
        self.restore_state = {"original_power_plan": self.get_power(), "level": level,
                              "game_path": game_path, "timestamp": datetime.now().isoformat()}
        save_restore_state(self.restore_state)

        self.set_power(level); step()
        res["ram_freed"] = self.optimize_ram(level); step()
        res["processes_killed"] = self.kill_bloat(level); step()
        res["services_stopped"] = self.stop_svcs(level); step()
        self.set_timer(level); step()
        self.disable_gb(); step()
        self.set_gpu(game_path); step()
        if level in ("medium", "max"): self.disable_nagle()
        step()
        if level in ("medium", "max"): self.opt_visual(level)
        step()
        self.flush_dns(); step()

        self._log("Launching game...", "info")
        try:
            exe = os.path.basename(game_path)
            proc = subprocess.Popen([game_path], cwd=os.path.dirname(game_path),
                                    creationflags=subprocess.HIGH_PRIORITY_CLASS)
            step()
            ap = self._wait_for_process_ready(proc.pid, exe, 60, 1.5); step()
            if ap:
                self.game_pid = ap; self._apply_proc_opts(ap, level)
                if level == "max": self.lower_bg()
            else: res["success"] = False
            step()
        except Exception as e:
            self._log(f"Launch failed: {e}", "error"); res["success"] = False; step()

        self.is_boosted = True; self._set_progress(1.0)
        self._log("═══ BOOST COMPLETE ═══", "success"); return res

    def restore_all(self):
        self._log("═══ RESTORING ═══", "info")
        self.restore_power(); self.restore_svcs(); self.restore_timer(); self.restore_nagle()
        self.game_pid = None; self.is_boosted = False
        if os.path.exists(RESTORE_FILE): os.remove(RESTORE_FILE)
        self._log("═══ RESTORED ═══", "success")


# ═══════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════

class QBoosterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        cfg = load_config()
        self.current_lang = cfg.get("language", "Türkçe")
        self.lang = LANGUAGES.get(self.current_lang, LANGUAGES["English"])

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1050x800")
        self.minsize(980, 760)
        self.configure(fg_color=COLORS["bg_dark"])

        # ══════════════════════════════════════
        # FULL HD LOGO YÜKLEME
        # ══════════════════════════════════════
        try:
            self.logos = get_or_create_logo()

            from PIL import ImageTk
            self._icon_photo = ImageTk.PhotoImage(self.logos["icon"])
            self.iconphoto(False, self._icon_photo)

            # CTkImage nesneleri (header için)
            self.header_logo = ctk.CTkImage(
                light_image=self.logos["header"],
                dark_image=self.logos["header"],
                size=(52, 52),
            )
        except Exception as e:
            print(f"Logo error: {e}")
            self.header_logo = None
            self.logos = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.game_path = ctk.StringVar(value="")
        self.boost_level = ctk.StringVar(value="medium")
        self.lang_var = ctk.StringVar(value=self.current_lang)

        self.optimizer = SystemOptimizer()
        self.optimizer.add_log_callback(self._safe_log)
        self.optimizer.add_progress_callback(self._safe_progress)
        self.monitor_active = True

        self._build_ui()
        self._start_monitor()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def t(self, key, **kw):
        txt = self.lang.get(key, key)
        if kw: txt = txt.format(**kw)
        return txt

    def _safe_log(self, m, l="info"): self.after(0, self.add_log, m, l)
    def _safe_progress(self, v): self.after(0, lambda: self.progress.set(v))

    def _change_lang(self, name):
        self.current_lang = name
        self.lang = LANGUAGES.get(name, LANGUAGES["English"])
        cfg = load_config(); cfg["language"] = name; save_config(cfg)
        for w in self.winfo_children(): w.destroy()
        self._build_ui()
        self.add_log(f"Language → {name}", "info")

    def _build_ui(self):
        # ═══════ HEADER (BÜYÜK LOGO) ═══════
        hdr = ctk.CTkFrame(self, fg_color=COLORS["accent_blue"], height=75, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        # ── HD Logo (52x52) ──
        if self.header_logo:
            ctk.CTkLabel(hdr, image=self.header_logo, text="").pack(
                side="left", padx=(20, 12), pady=10)

        ctk.CTkLabel(hdr, text=APP_NAME,
                     font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                     text_color=COLORS["accent"]).pack(side="left", pady=15)

        ctk.CTkLabel(hdr, text=APP_VERSION, font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(10, 0), pady=(22, 0))

        # Dil seçici
        lf = ctk.CTkFrame(hdr, fg_color="transparent"); lf.pack(side="right", padx=15)
        ctk.CTkLabel(lf, text=self.t("language"), font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 5))
        ctk.CTkOptionMenu(lf, values=list(LANGUAGES.keys()), variable=self.lang_var,
                          command=self._change_lang, width=120, height=30,
                          font=ctk.CTkFont(size=12), fg_color=COLORS["btn_secondary"],
                          button_color=COLORS["accent_blue_light"],
                          button_hover_color=COLORS["btn_secondary_hover"],
                          dropdown_fg_color=COLORS["bg_card"],
                          dropdown_hover_color=COLORS["accent_blue_light"]).pack(side="left")

        # ═══════ ANA İÇERİK ═══════
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=10)
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 7))
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(7, 0))

        # ── Oyun Seçimi ──
        gc = self._card(left, self.t("game_select"))
        gr = ctk.CTkFrame(gc, fg_color="transparent"); gr.pack(fill="x", padx=15, pady=(5, 15))
        self.game_entry = ctk.CTkEntry(gr, textvariable=self.game_path,
                                       placeholder_text=self.t("browse_placeholder"),
                                       height=40, font=ctk.CTkFont(size=13),
                                       fg_color=COLORS["bg_dark"], border_color=COLORS["border"])
        self.game_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(gr, text=self.t("browse"), width=100, height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_primary_hover"],
                      command=self._browse).pack(side="right")

        # ── Boost Seviyesi ──
        bc = self._card(left, self.t("boost_level"))
        for val, tkey, dkey, col in [
            ("low", "low_title", "low_desc", COLORS["boost_low"]),
            ("medium", "mid_title", "mid_desc", COLORS["boost_mid"]),
            ("max", "max_title", "max_desc", COLORS["boost_max"])]:
            f = ctk.CTkFrame(bc, fg_color=COLORS["bg_dark"], corner_radius=8,
                             border_width=1, border_color=COLORS["border"])
            f.pack(fill="x", padx=15, pady=4)
            ctk.CTkRadioButton(f, text=self.t(tkey), variable=self.boost_level, value=val,
                               font=ctk.CTkFont(size=14, weight="bold"),
                               text_color=col, fg_color=col, hover_color=col,
                               border_color=COLORS["border"]).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(f, text=self.t(dkey), font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_dim"], justify="left").pack(anchor="w", padx=38, pady=(0, 10))

        # ── Ana Butonlar ──
        bf = ctk.CTkFrame(left, fg_color="transparent"); bf.pack(fill="x", pady=(10, 0))
        self.boost_btn = ctk.CTkButton(bf, text=self.t("boost_btn"), height=50,
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_primary_hover"],
                                       command=self._boost_thread)
        self.boost_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.restore_btn = ctk.CTkButton(bf, text=self.t("restore_btn"), height=50,
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         fg_color=COLORS["btn_secondary"], hover_color=COLORS["btn_secondary_hover"],
                                         border_width=1, border_color=COLORS["border"],
                                         command=self._restore_thread)
        self.restore_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ── Araçlar ──
        tc = self._card(left, self.t("tools"))
        
        # İlk satır: DNS + Junk
        tr1 = ctk.CTkFrame(tc, fg_color="transparent"); tr1.pack(fill="x", padx=15, pady=(5, 5))
        self.dns_btn = ctk.CTkButton(tr1, text=self.t("dns_btn"), height=40,
                                     font=ctk.CTkFont(size=13, weight="bold"),
                                     fg_color=COLORS["accent_blue_light"],
                                     hover_color=COLORS["btn_secondary_hover"],
                                     command=self._dns_thread)
        self.dns_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.junk_btn = ctk.CTkButton(tr1, text=self.t("junk_btn"), height=40,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      fg_color=COLORS["btn_danger"], hover_color=COLORS["btn_danger_hover"],
                                      command=self._junk_thread)
        self.junk_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # İkinci satır: Ultimate Performance (tek buton, tam genişlik)
        tr2 = ctk.CTkFrame(tc, fg_color="transparent"); tr2.pack(fill="x", padx=15, pady=(0, 15))
        self.ultimate_btn = ctk.CTkButton(tr2, text=self.t("ultimate_btn"), height=45,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         fg_color=COLORS["accent"], 
                                         hover_color=COLORS["accent_hover"],
                                         text_color=COLORS["bg_dark"],
                                         command=self._ultimate_thread)
        self.ultimate_btn.pack(fill="x")

        self.progress = ctk.CTkProgressBar(left, height=6, fg_color=COLORS["bg_card"],
                                           progress_color=COLORS["accent"])
        self.progress.pack(fill="x", pady=(10, 0)); self.progress.set(0)

        # ── Monitör ──
        mc = self._card(right, self.t("monitor"))
        for label, attr, dc in [("CPU", "cpu", COLORS["accent"]),
                                ("RAM", "ram", COLORS["success"]),
                                ("DISK", "disk", COLORS["warning"])]:
            row = ctk.CTkFrame(mc, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=(5 if label == "CPU" else 0, 8))
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dim"], width=50).pack(side="left")
            bar = ctk.CTkProgressBar(row, height=18, fg_color=COLORS["bg_dark"],
                                     progress_color=dc, corner_radius=4)
            bar.pack(side="left", fill="x", expand=True, padx=10); bar.set(0)
            setattr(self, f"{attr}_bar", bar)
            lbl = ctk.CTkLabel(row, text="0%", font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=COLORS["text"], width=90 if attr == "ram" else 50)
            lbl.pack(side="right"); setattr(self, f"{attr}_label", lbl)

        self.status_label = ctk.CTkLabel(mc, text=self.t("status_idle"),
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color=COLORS["text_dim"])
        self.status_label.pack(pady=(0, 15))

        # ── Log ──
        lc = self._card(right, self.t("log_title"), expand=True)
        self.log_box = ctk.CTkTextbox(lc, font=ctk.CTkFont(family="Consolas", size=12),
                                      fg_color=COLORS["bg_dark"], text_color=COLORS["text"],
                                      border_width=1, border_color=COLORS["border"],
                                      corner_radius=6, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        for tag, clr in [("success", COLORS["success"]), ("warning", COLORS["warning"]),
                         ("error", COLORS["error"]), ("info", COLORS["text_dim"])]:
            self.log_box.tag_config(tag, foreground=clr)

        self.add_log(self.t("started", ver=APP_VERSION), "info")

    def _card(self, parent, title, expand=False):
        c = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        c.pack(fill="both", expand=expand, pady=(0, 10))
        ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkFrame(c, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=15, pady=(0, 5))
        return c

    def _browse(self):
        p = filedialog.askopenfilename(title=self.t("browse_dialog_title"),
                                       filetypes=[("Game", "*.exe"), ("All", "*.*")])
        if p: self.game_path.set(p); self.add_log(self.t("game_selected", name=os.path.basename(p)), "info")

    def add_log(self, msg, level="info"):
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            icons = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[{ts}] {icons.get(level, 'ℹ️')} ", "info")
            self.log_box.insert("end", f"{msg}\n", level)
            self.log_box.see("end"); self.log_box.configure(state="disabled")
        except: pass

    def _start_monitor(self):
        def loop():
            while self.monitor_active:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    m = psutil.virtual_memory()
                    ru, rt, rp = m.used/(1024**3), m.total/(1024**3), m.percent/100
                    try: dp = psutil.disk_usage("/").percent / 100
                    except: dp = 0
                    self.after(0, self._upd_mon, cpu, ru, rt, rp, dp)
                except: pass
        threading.Thread(target=loop, daemon=True).start()

    def _upd_mon(self, cpu, ru, rt, rp, dp):
        try:
            self.cpu_bar.set(cpu/100); self.cpu_label.configure(text=f"{cpu:.0f}%")
            self.cpu_bar.configure(progress_color=COLORS["success"] if cpu < 60 else COLORS["warning"] if cpu < 85 else COLORS["error"])
            self.ram_bar.set(rp); self.ram_label.configure(text=f"{ru:.1f}/{rt:.0f} GB")
            self.ram_bar.configure(progress_color=COLORS["success"] if rp < 0.7 else COLORS["warning"] if rp < 0.9 else COLORS["error"])
            self.disk_bar.set(dp); self.disk_label.configure(text=f"{dp*100:.0f}%")
        except: pass

    def _boost_thread(self):
        g = self.game_path.get()
        if not g or not os.path.isfile(g):
            messagebox.showwarning(self.t("no_game_title"), self.t("no_game")); return
        if self.optimizer.is_boosted:
            if not messagebox.askyesno(self.t("boost_exists_title"), self.t("boost_exists")): return
            self.optimizer.restore_all()
        self.boost_btn.configure(state="disabled", text=self.t("boosting"))
        self.restore_btn.configure(state="disabled"); self.progress.set(0)
        def run():
            lv = self.boost_level.get(); r = self.optimizer.apply_boost(g, lv)
            ns = {"low": self.t("level_low"), "medium": self.t("level_mid"), "max": self.t("level_max")}
            cs = {"low": COLORS["boost_low"], "medium": COLORS["boost_mid"], "max": COLORS["boost_max"]}
            def upd():
                self.boost_btn.configure(state="normal", text=self.t("boost_btn"))
                self.restore_btn.configure(state="normal")
                if r["success"]:
                    self.status_label.configure(text=self.t("status_active", level=ns[lv]), text_color=cs[lv])
                    self.add_log(self.t("summary", ram=f"{r['ram_freed']:.0f}",
                                       svc=r['services_stopped'], proc=r['processes_killed']), "success")
                else:
                    self.status_label.configure(text=self.t("status_partial"), text_color=COLORS["warning"])
            self.after(0, upd)
        threading.Thread(target=run, daemon=True).start()

    def _restore_thread(self):
        if not self.optimizer.is_boosted:
            messagebox.showinfo("Info", self.t("no_restore")); return
        self.restore_btn.configure(state="disabled", text=self.t("restoring"))
        def run():
            self.optimizer.restore_all()
            def upd():
                self.restore_btn.configure(state="normal", text=self.t("restore_btn"))
                self.status_label.configure(text=self.t("status_idle"), text_color=COLORS["text_dim"])
                self.progress.set(0)
            self.after(0, upd)
        threading.Thread(target=run, daemon=True).start()

    def _dns_thread(self):
        self.dns_btn.configure(state="disabled")
        def run():
            ok = self.optimizer.flush_dns()
            def upd():
                self.dns_btn.configure(state="normal")
                self.add_log(self.t("dns_success") if ok else self.t("dns_fail", err="Access"), "success" if ok else "error")
            self.after(0, upd)
        threading.Thread(target=run, daemon=True).start()

    def _junk_thread(self):
        if not messagebox.askyesno(self.t("junk_confirm_title"), self.t("junk_confirm")): return
        self.junk_btn.configure(state="disabled")
        def run():
            try:
                r = self.optimizer.clean_junk()
                def upd():
                    self.junk_btn.configure(state="normal")
                    self.add_log(self.t("junk_success", count=r["count"], size=f"{r['size_mb']:.1f}"), "success")
                self.after(0, upd)
            except Exception as e:
                def err():
                    self.junk_btn.configure(state="normal")
                    self.add_log(self.t("junk_fail", err=str(e)), "error")
                self.after(0, err)
        threading.Thread(target=run, daemon=True).start()

    def _ultimate_thread(self):
        """Nihai Performans modunu aktif eder"""
        self.ultimate_btn.configure(state="disabled")
        
        def run():
            success = self.optimizer.activate_ultimate_performance()
            
            def upd():
                self.ultimate_btn.configure(state="normal")
                if success:
                    # Başarılı - yeşil log
                    self.add_log(self.t("ultimate_success"), "success")
                else:
                    # Hata - kırmızı log
                    self.add_log(self.t("ultimate_error"), "error")
            
            self.after(0, upd)
        
        threading.Thread(target=run, daemon=True).start()

    def _on_close(self):
        self.monitor_active = False
        if self.optimizer.is_boosted:
            if messagebox.askyesno(self.t("close_title"), self.t("close_confirm")):
                self.optimizer.restore_all()
        self.destroy()


def main():
    if not is_admin():
        if messagebox.askyesno(APP_NAME, "Administrator privileges required.\nRestart as Admin?"):
            run_as_admin(); return
    ensure_config_dir()
    QBoosterApp().mainloop()

if __name__ == "__main__":
    main()
