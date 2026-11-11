// lib/core/localization/translations.dart

class Translations {
  static const Map<String, Map<String, String>> localizedValues = {
    'en': {
      'app_title': 'Vemavaram Smart Village',
      'new_complaint': 'New Complaint',
      'my_complaints': 'My Complaints',
      'category': 'Category',
      'description': 'Description',
      'submit': 'Submit',
      'offline_warning': 'You are offline. Complaint saved and will sync later.',
    },
    'te': {
      'app_title': 'వేమవరం స్మార్ట్ విలేజ్',
      'new_complaint': 'కొత్త ఫిర్యాదు',
      'my_complaints': 'నా ఫిర్యాదులు',
      'category': 'వర్గం',
      'description': 'వివరణ',
      'submit': 'సమర్పించండి',
      'offline_warning': 'మీరు ఆఫ్‌లైన్‌లో ఉన్నారు. ఫిర్యాదు సేవ్ చేయబడింది.',
    },
    'hi': {
      'app_title': 'वेमावरम स्मार्ट विलेज',
      'new_complaint': 'नई शिकायत',
      'my_complaints': 'मेरी शिकायतें',
      'category': 'श्रेणी',
      'description': 'विवरण',
      'submit': 'जमा करें',
      'offline_warning': 'आप ऑफ़लाइन हैं। शिकायत सहेज ली गई है।',
    }
  };

  static String currentLang = 'en';

  static String get(String key) {
    return localizedValues[currentLang]?[key] ?? key;
  }
}
