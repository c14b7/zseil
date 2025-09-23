#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do anonimizacji danych w pliku data.json
Zmienia pełne nazwiska nauczycieli na inicjały.
"""

import json
import re
from typing import Dict, Any

def create_initials(full_name: str) -> str:
    """
    Konwertuje pełne nazwisko na inicjały.
    
    Args:
        full_name (str): Pełne nazwisko, np. "GÓRSKA MARZANNA"
    
    Returns:
        str: Inicjały, np. "G.M."
    """
    # Usuń dodatkowe spacje i podziel na słowa
    words = full_name.strip().split()
    
    # Weź pierwszą literę każdego słowa
    initials = [word[0] for word in words if word]
    
    # Połącz inicjały kropkami
    return ".".join(initials) + "."

def anonymize_teacher_names(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anonimizuje nazwiska nauczycieli w całej strukturze danych.
    
    Args:
        data (Dict): Dane z pliku JSON
    
    Returns:
        Dict: Zmodyfikowane dane z inicjałami
    """
    # Mapowanie pełnych nazwisk na inicjały
    teacher_mapping = {}
    
    # Najpierw utworz mapowanie dla wszystkich nauczycieli z sekcji "nauczyciel"
    if "available_items" in data and "nauczyciel" in data["available_items"]:
        for teacher_name in data["available_items"]["nauczyciel"]:
            initials = create_initials(teacher_name)
            teacher_mapping[teacher_name] = initials
        
        # Zamień nazwiska w sekcji available_items
        data["available_items"]["nauczyciel"] = [
            teacher_mapping[name] for name in data["available_items"]["nauczyciel"]
        ]
    
    # Funkcja rekurencyjna do przeglądania i zamiany w harmonogramach
    def replace_in_schedules(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "teacher" and isinstance(value, str):
                    # Zamień nazwisko nauczyciela na inicjały
                    if value in teacher_mapping:
                        obj[key] = teacher_mapping[value]
                    else:
                        # Jeśli nie ma w mapowaniu, utwórz inicjały na miejscu
                        obj[key] = create_initials(value)
                else:
                    replace_in_schedules(value)
        elif isinstance(obj, list):
            for item in obj:
                replace_in_schedules(item)
    
    # Przetwórz wszystkie harmonogramy
    if "schedules" in data:
        replace_in_schedules(data["schedules"])
    
    return data

def main():
    """
    Główna funkcja skryptu.
    """
    input_file = "data.json"
    output_file = "data.json"  # Nadpisujemy oryginalny plik
    backup_file = "data_backup.json"
    
    try:
        print(f"Wczytywanie pliku {input_file}...")
        
        # Wczytaj dane
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Tworzenie kopii zapasowej...")
        # Utwórz kopię zapasową
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("Anonimizacja nazwisk nauczycieli...")
        
        # Policz oryginalne nazwiska
        original_teachers = set()
        if "available_items" in data and "nauczyciel" in data["available_items"]:
            original_teachers = set(data["available_items"]["nauczyciel"])
        
        # Anonimizuj dane
        anonymized_data = anonymize_teacher_names(data)
        
        print("Zapisywanie zmodyfikowanych danych...")
        
        # Zapisz zmodyfikowane dane
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(anonymized_data, f, ensure_ascii=False, indent=2)
        
        # Pokaż statystyki
        new_teachers = set()
        if "available_items" in anonymized_data and "nauczyciel" in anonymized_data["available_items"]:
            new_teachers = set(anonymized_data["available_items"]["nauczyciel"])
        
        print(f"\n✅ Anonimizacja zakończona pomyślnie!")
        print(f"📊 Statystyki:")
        print(f"   - Przetworzono {len(original_teachers)} unikalnych nazwisk nauczycieli")
        print(f"   - Utworzono {len(new_teachers)} unikalnych inicjałów")
        print(f"   - Kopia zapasowa zapisana jako: {backup_file}")
        print(f"   - Zmodyfikowane dane zapisane w: {output_file}")
        
        # Pokaż przykłady zmian
        print(f"\n📝 Przykłady zmian:")
        sample_changes = list(zip(
            list(original_teachers)[:5], 
            [create_initials(name) for name in list(original_teachers)[:5]]
        ))
        for original, anonymized in sample_changes:
            print(f"   {original} → {anonymized}")
        
        if len(original_teachers) > 5:
            print(f"   ... i {len(original_teachers) - 5} więcej")
            
    except FileNotFoundError:
        print(f"❌ Błąd: Nie znaleziono pliku {input_file}")
        print("Upewnij się, że plik data.json znajduje się w tym samym katalogu co skrypt.")
    except json.JSONDecodeError as e:
        print(f"❌ Błąd: Nieprawidłowy format JSON w pliku {input_file}")
        print(f"Szczegóły: {e}")
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    main()