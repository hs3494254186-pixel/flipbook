/**
 * Small UI-string localization layer for the visible app chrome.
 * Generated page titles, labels, and click subjects are localized by the
 * backend via `output_locale`; this file covers controls around the canvas.
 */

export type LocaleStrings = {
  placeholder: string;
  upload: string;
  go: string;
  generating: string;
  animateClip: string;
  animateStream: string;
  animateStop: string;
  generatingClip: string;
  edit: string;
  cancelEdit: string;
  apply: string;
  editPlaceholder: string;
  tapHint: string;
  langLabel: string;
  langAuto: string;
  themeLight: string;
  themeGraphite: string;
  themeDark: string;
};

const en: LocaleStrings = {
  placeholder: "Ask about anything, or upload a seed image...",
  upload: "Upload",
  go: "Go",
  generating: "...",
  animateClip: "Animate (5s clip)",
  animateStream: "Animate (stream)",
  animateStop: "Stop",
  generatingClip: "Generating clip...",
  edit: "Edit",
  cancelEdit: "Cancel edit",
  apply: "Apply",
  editPlaceholder: "Describe how to change this image...",
  tapHint: "Click anywhere on the image to explore.",
  langLabel: "Output language",
  langAuto: "auto",
  themeLight: "light",
  themeGraphite: "graphite",
  themeDark: "dark",
};

const STRINGS: Record<string, Partial<LocaleStrings>> = {
  en,
  es: {
    placeholder: "Pregunta cualquier cosa o sube una imagen base...",
    upload: "Subir",
    go: "Ir",
    animateClip: "Animar (5s)",
    animateStream: "Animar (stream)",
    animateStop: "Detener",
    generatingClip: "Generando clip...",
    edit: "Editar",
    cancelEdit: "Cancelar edicion",
    apply: "Aplicar",
    editPlaceholder: "Describe como modificar esta imagen...",
    tapHint: "Haz clic en la imagen para explorar.",
    langLabel: "Idioma de salida",
    langAuto: "auto",
    themeLight: "claro",
    themeGraphite: "grafito",
    themeDark: "oscuro",
  },
  fr: {
    placeholder: "Posez une question ou importez une image de depart...",
    upload: "Importer",
    go: "Aller",
    animateClip: "Animer (5s)",
    animateStream: "Animer (stream)",
    animateStop: "Arreter",
    generatingClip: "Generation du clip...",
    edit: "Modifier",
    cancelEdit: "Annuler",
    apply: "Appliquer",
    editPlaceholder: "Decrivez comment modifier cette image...",
    tapHint: "Cliquez sur l'image pour explorer.",
    langLabel: "Langue de sortie",
    langAuto: "auto",
    themeLight: "clair",
    themeGraphite: "graphite",
    themeDark: "sombre",
  },
  de: {
    placeholder: "Frag etwas oder lade ein Startbild hoch...",
    upload: "Hochladen",
    go: "Los",
    animateClip: "Animieren (5s)",
    animateStream: "Animieren (Stream)",
    animateStop: "Stopp",
    generatingClip: "Erzeuge Clip...",
    edit: "Bearbeiten",
    cancelEdit: "Abbrechen",
    apply: "Anwenden",
    editPlaceholder: "Beschreibe die Aenderung...",
    tapHint: "Klicke ins Bild, um zu erkunden.",
    langLabel: "Ausgabesprache",
    langAuto: "auto",
    themeLight: "hell",
    themeGraphite: "graphit",
    themeDark: "dunkel",
  },
  tr: {
    placeholder: "Bir sey sor veya baslangic gorseli yukle...",
    upload: "Yukle",
    go: "Git",
    animateClip: "Animasyon (5s)",
    animateStream: "Animasyon (akis)",
    animateStop: "Durdur",
    generatingClip: "Klip olusturuluyor...",
    edit: "Duzenle",
    cancelEdit: "Iptal",
    apply: "Uygula",
    editPlaceholder: "Bu gorseli nasil degistirecegini anlat...",
    tapHint: "Kesfetmek icin gorsele tikla.",
    langLabel: "Cikti dili",
    langAuto: "oto",
    themeLight: "acik",
    themeGraphite: "grafit",
    themeDark: "koyu",
  },
  ja: {
    placeholder: "質問するか、開始画像をアップロード...",
    upload: "アップロード",
    go: "開始",
    animateClip: "アニメ化 (5秒)",
    animateStream: "アニメ化 (ストリーム)",
    animateStop: "停止",
    generatingClip: "クリップ生成中...",
    edit: "編集",
    cancelEdit: "編集をキャンセル",
    apply: "適用",
    editPlaceholder: "この画像をどう変更するか説明...",
    tapHint: "画像をクリックして探索。",
    langLabel: "出力言語",
    langAuto: "自動",
    themeLight: "ライト",
    themeGraphite: "グラファイト",
    themeDark: "ダーク",
  },
  zh: {
    placeholder: "输入任意主题，或上传一张起始图片...",
    upload: "上传",
    go: "开始",
    generating: "生成中...",
    animateClip: "动画 (5秒)",
    animateStream: "动画 (流式)",
    animateStop: "停止",
    generatingClip: "正在生成片段...",
    edit: "编辑",
    cancelEdit: "取消编辑",
    apply: "应用",
    editPlaceholder: "描述你想如何修改这张图...",
    tapHint: "点击图片任意区域继续探索。",
    langLabel: "输出语言",
    langAuto: "自动",
    themeLight: "浅色",
    themeGraphite: "石墨",
    themeDark: "深色",
  },
  ar: {
    placeholder: "اسأل عن أي شيء أو ارفع صورة بداية...",
    upload: "رفع",
    go: "ابدأ",
    animateClip: "تحريك (5 ثوان)",
    animateStream: "تحريك (بث)",
    animateStop: "إيقاف",
    generatingClip: "يتم إنشاء المقطع...",
    edit: "تعديل",
    cancelEdit: "إلغاء التعديل",
    apply: "تطبيق",
    editPlaceholder: "صف كيف تريد تغيير هذه الصورة...",
    tapHint: "انقر على الصورة لاستكشافها.",
    langLabel: "لغة الإخراج",
    langAuto: "تلقائي",
    themeLight: "فاتح",
    themeGraphite: "غرافيت",
    themeDark: "داكن",
  },
};

export const SUPPORTED_LOCALES = [
  "auto",
  "en",
  "es",
  "fr",
  "de",
  "tr",
  "ja",
  "zh",
  "ar",
] as const;

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

const RTL_LOCALES = new Set(["ar", "he", "fa", "ur"]);

function shortTag(locale: string): string {
  const head = locale.split("-")[0] ?? "en";
  return head.toLowerCase();
}

export function isRTL(locale: string): boolean {
  return RTL_LOCALES.has(shortTag(locale));
}

export function detectLocale(): SupportedLocale {
  if (typeof navigator === "undefined") return "auto";
  const short = shortTag(navigator.language || "en");
  return (SUPPORTED_LOCALES as readonly string[]).includes(short)
    ? (short as SupportedLocale)
    : "auto";
}

export function getStrings(locale: string): LocaleStrings {
  let key = shortTag(locale);
  if (key === "auto") {
    key =
      typeof navigator !== "undefined"
        ? shortTag(navigator.language || "en")
        : "en";
  }
  const table = STRINGS[key] ?? {};
  return { ...en, ...table };
}

export function resolveOutputLocale(uiLocale: string): string {
  if (uiLocale === "auto") {
    return typeof navigator !== "undefined"
      ? shortTag(navigator.language || "en")
      : "en";
  }
  return uiLocale;
}
