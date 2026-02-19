#!/usr/bin/env python3
"""
Script para ejecutar migraciones SQL en SQLite.

Uso:
    python3 scripts/init_migrations.py
"""

import os
import sqlite3
from pathlib import Path

def run_migrations():
    """Ejecuta todas las migraciones SQL en orden"""
    
    # Paths
    db_path = 'academy.db'
    migrations_dir = Path('migrations')
    
    # Listar migraciones
    migration_files = sorted([
        f for f in migrations_dir.glob('*.sql')
        if f.name.startswith(tuple('0123456789'))
    ])
    
    if not migration_files:
        print("⚠️  No hay migraciones para ejecutar")
        return
    
    try:
        # Conectar a BD
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"✅ Conectado a {db_path}")
        
        # Ejecutar cada migración
        for migration_file in migration_files:
            print(f"\n📝 Ejecutando: {migration_file.name}")
            
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            try:
                cursor.executescript(sql_content)
                conn.commit()
                print(f"✅ {migration_file.name} ejecutada correctamente")
            except Exception as e:
                conn.rollback()
                print(f"❌ Error en {migration_file.name}: {str(e)}")
                raise
        
        # Mostrar resumen de tablas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("✅ Todas las migraciones ejecutadas correctamente")
        print("="*50)
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in tables:
            print(f"   • {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == '__main__':
    run_migrations()