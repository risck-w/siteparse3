from db.mysql import sessions
from models.products import ParseLog
from sqlalchemy import desc
from db.mongo import ParserRank


def sync_data():
    session = sessions()
    sql = """
        select * 
        from parse_log t1 
        where exists (
            select count(*)
            from parse_log t2 
            where t2.pdt_type = t1.pdt_type and  t1.info_num > t2.info_num HAVING count(*) < 10
        ) order by t1.info_num desc
        
    """
    filter_data = session.execute(sql)
    filter_data = [dict(x.items()) for x in filter_data.fetchall()]

    ParserRank.drop_collection()
    for query in filter_data:
        result = ParserRank.objects(name=query['name']).update(author=query['author'], pdt_type=query['pdt_type'], info_num=query['info_num'])
        if result != 1:
            ParserRank(name=query['name'],
                       author=query['author'],
                       pdt_type=query['pdt_type'],
                       info_num=query['info_num']).save()
