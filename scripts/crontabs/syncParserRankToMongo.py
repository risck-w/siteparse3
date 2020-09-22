from db.mysql import sessions
from models.products import ParseLog
from sqlalchemy import desc
from db.mongo import ParserRank


def sync_data():
    session = sessions()
    params = ['name', 'author', 'pdt_type', 'info_num']
    filter_data = session.query(ParseLog).order_by(desc(ParseLog.info_num)).limit(10).all()
    filter_data = [x.to_json(params) for x in filter_data]
    print (filter_data)

    ParserRank.drop_collection()
    for query in filter_data:
        result = ParserRank.objects(name=query['name']).update(author=query['author'], pdt_type=query['pdt_type'], info_num=query['info_num'])
        if result != 1:
            ParserRank(name=query['name'],
                       author=query['author'],
                       pdt_type=query['pdt_type'],
                       info_num=query['info_num']).save()
