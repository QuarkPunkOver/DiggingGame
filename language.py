import json
import os

class Language:
    def __init__(self):
        self._settings = None
        self.current_lang = 'en'
        self.strings = {}
    
    @property
    def settings(self):
        if self._settings is None:
            from settings import settings
            self._settings = settings
        return self._settings
    
    def initialize(self):
        self.current_lang = self.settings.language
        self.load_language(self.current_lang)
    
    def load_language(self, lang_code):
        try:
            lang_file = os.path.join('lang', f'{lang_code}.json')
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
            self.current_lang = lang_code
            print(f"[LANG] Loaded language: {lang_code}")
        except Exception as e:
            print(f"[LANG] Error loading {lang_code}: {e}")
            try:
                with open(os.path.join('lang', 'en.json'), 'r', encoding='utf-8') as f:
                    self.strings = json.load(f)
                self.current_lang = 'en'
            except:
                self.strings = {}
    
    def get(self, key, **kwargs):
        if not self.strings:
            self.initialize()
        text = self.strings.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
    
    def set_language(self, lang_code):
        self.load_language(lang_code)
        self.settings.language = lang_code
        self.settings.save()

lang = Language()