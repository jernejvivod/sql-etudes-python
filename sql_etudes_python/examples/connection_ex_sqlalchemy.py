from sqlalchemy import create_engine, MetaData, Table

if __name__ == '__main__':
    engine = create_engine('postgresql+pg8000://postgres:postgres@localhost:5432/employees')
    conn = engine.connect()
    metadata = MetaData(schema='employees')
    table = Table(
        'departments',
        metadata,
        autoload=True,
        autoload_with=engine
    )

    s = table.select()
    result = conn.execute(s).fetchall()
    conn.close()
    engine.dispose()
