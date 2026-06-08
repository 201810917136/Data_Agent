import random
from datetime import datetime, timedelta

# SQL to insert seed data
def generate_seed_sql():
    sql_lines = []
    
    # Areas
    areas = [
        (1, '北京', '北京市', '北京市'),
        (2, '上海', '上海市', '上海市'),
        (3, '广州', '广东省', '广州市'),
        (4, '深圳', '广东省', '深圳市'),
        (5, '成都', '四川省', '成都市'),
        (6, '杭州', '浙江省', '杭州市'),
        (7, '武汉', '湖北省', '武汉市'),
        (8, '南京', '江苏省', '南京市'),
    ]
    for a in areas:
        sql_lines.append(f"INSERT INTO dim_areas (id, name, province, city) VALUES ({a[0]}, '{a[1]}', '{a[2]}', '{a[3]}') ON CONFLICT DO NOTHING;")
    
    # Stores
    stores = [
        (1, '北京朝阳店', 1), (2, '北京海淀店', 1), (3, '上海浦东店', 2),
        (4, '上海闵行店', 2), (5, '广州天河店', 3), (6, '深圳南山店', 4),
        (7, '成都锦江店', 5), (8, '杭州西湖店', 6), (9, '武汉江汉店', 7),
        (10, '南京鼓楼店', 8),
    ]
    for s in stores:
        sql_lines.append(f"INSERT INTO dim_stores (id, name, area_id) VALUES ({s[0]}, '{s[1]}', {s[2]}) ON CONFLICT DO NOTHING;")
    
    # Employees
    roles = ['dealer', 'admin', 'inspector', 'manager']
    for i in range(1, 51):
        store_id = (i % 10) + 1
        role = random.choice(roles)
        sql_lines.append(f"INSERT INTO dim_employees (id, name, store_id, role) VALUES ({i}, '\u5458\u5de5{i}', {store_id}, '{role}') ON CONFLICT DO NOTHING;")
    
    # DWS daily data - last 30 days
    today = datetime.now().date()
    for days_ago in range(30):
        stat_date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        for store_id in range(1, 11):
            total_amount = random.randint(50000000, 500000000)  # 50万-500万
            auction_count = random.randint(10, 100)
            sold_count = int(auction_count * random.uniform(0.5, 0.9))
            unsold_count = auction_count - sold_count
            avg_bid = total_amount // auction_count if auction_count else 0
            sql_lines.append(
                f"INSERT INTO dws_ucar_store_aution_1d (store_id, stat_date, total_amount, auction_count, sold_count, unsold_count, avg_bid_amount) "
                f"VALUES ({store_id}, '{stat_date}', {total_amount}, {auction_count}, {sold_count}, {unsold_count}, {avg_bid}) "
                f"ON CONFLICT (store_id, stat_date) DO NOTHING;"
            )
    
    # DWS monthly data
    for month_offset in range(6):
        d = today.replace(day=1) - timedelta(days=month_offset * 30)
        stat_month = d.strftime('%Y-%m')
        for store_id in range(1, 11):
            total = random.randint(1500000000, 15000000000)
            count = random.randint(300, 3000)
            sold = int(count * random.uniform(0.5, 0.9))
            sql_lines.append(
                f"INSERT INTO dws_ucar_auction_stores_1m (store_id, stat_month, total_amount, auction_count, sold_count) "
                f"VALUES ({store_id}, '{stat_month}', {total}, {count}, {sold}) "
                f"ON CONFLICT (store_id, stat_month) DO NOTHING;"
            )
    
    # Semantic layer metadata
    metadata = [
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'total_amount', '销售额,成交额,GMV', '拍卖总金额（分）', 'DWS'),
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'auction_count', '拍卖场次,上拍量', '拍卖场次数量', 'DWS'),
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'sold_count', '成交量', '成交数量', 'DWS'),
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'unsold_count', '流拍量', '流拍数量', 'DWS'),
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'stat_date', '日期', '统计日期', 'DWS'),
        ('dws_ucar_store_aution_1d', '门店拍卖日汇总表', 'store_id', None, '门店ID', 'DWS'),
        ('dws_ucar_auction_stores_1m', '门店拍卖月汇总表', 'total_amount', '月度销售额,月度GMV', '月度拍卖总金额（分）', 'DWS'),
        ('dws_ucar_auction_stores_1m', '门店拍卖月汇总表', 'stat_month', '月份', '统计月份', 'DWS'),
        ('dim_stores', '门店维度表', 'name', '门店名称', '门店名称', 'DIM'),
        ('dim_stores', '门店维度表', 'id', '门店ID', '门店ID', 'DIM'),
        ('dim_stores', '门店维度表', 'area_id', None, '地区ID', 'DIM'),
        ('dim_areas', '地区维度表', 'name', '地区名称,城市', '地区名称', 'DIM'),
        ('dim_areas', '地区维度表', 'province', '省份', '省份', 'DIM'),
        ('dim_areas', '地区维度表', 'city', '城市', '城市', 'DIM'),
        ('dim_employees', '员工维度表', 'name', '员工姓名', '员工姓名', 'DIM'),
        ('dim_employees', '员工维度表', 'role', '角色', '员工角色', 'DIM'),
    ]
    for m in metadata:
        terms = "ARRAY[" + ",".join([f"'{t}'" for t in m[3].split(',')]) + "]" if m[3] else "NULL"
        sql_lines.append(
            f"INSERT INTO sql_schema_metadata (table_name, table_comment, column_name, business_terms, column_comment, layer) "
            f"VALUES ('{m[0]}', '{m[1]}', '{m[2]}', {terms}, '{m[4]}', '{m[5]}');"
        )
    
    # Query examples (Few-shot)
    examples = [
        ('昨日各门店销售额', 'SELECT s.name, d.total_amount FROM dws_ucar_store_aution_1d d JOIN dim_stores s ON d.store_id = s.id WHERE d.stat_date = CURRENT_DATE - 1', 'DWS', 'ARRAY[\'GMV\',\'门店\',\'日\']'),
        ('本月成交率', 'SELECT SUM(sold_count)::float / NULLIF(SUM(auction_count), 0) FROM dws_ucar_store_aution_1d WHERE stat_date >= DATE_TRUNC(\'month\', CURRENT_DATE)', 'DWS', 'ARRAY[\'成交率\',\'月\']'),
    ]
    for e in examples:
        sql_lines.append(f"INSERT INTO query_examples (question, sql, layer, tags) VALUES ('{e[0]}', '{e[1]}', '{e[2]}', {e[3]});")
    
    # Default user permissions
    sql_lines.append("INSERT INTO user_permissions (user_id, role, allowed_tables, allowed_columns, denied_columns) VALUES ('admin', 'admin', ARRAY['dws_ucar_store_aution_1d','dws_ucar_auction_stores_1m','dim_stores','dim_areas','dim_employees','dwd_ucar_auction_orders_di'], NULL, NULL);")
    sql_lines.append("INSERT INTO user_permissions (user_id, role, allowed_tables, allowed_columns, denied_columns) VALUES ('user1', 'user', ARRAY['dws_ucar_store_aution_1d','dim_stores','dim_areas'], NULL, ARRAY['total_amount']);")
    
    return '\n'.join(sql_lines)

if __name__ == '__main__':
    sql = generate_seed_sql()
    with open('data/seed_data.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    print(f'Generated seed_data.sql with {len(sql.splitlines())} lines')
