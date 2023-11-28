from sqlalchemy import Column, DateTime, Integer, TEXT, VARCHAR, BigInteger
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

DeclBase = declarative_base(metaclass=BindKeyMeta)
metadata = DeclBase.metadata


def create_sql():
    import setting
    # 创建数据库
    from sqlalchemy import create_engine
    engine = create_engine(setting.DB_URL, echo=True)

    if "xxxxxx" not in setting.DB_URL:
        DeclBase.metadata.drop_all(engine)  # 删除所有表

    DeclBase.metadata.create_all(engine)  # 创建数据库
    return engine
class MpLog27516(DeclBase):
    __tablename__ = 'log_27516'

    id = Column(Integer, primary_key=True, autoincrement=True)
    actiontype_ = Column(BigInteger)
    messageid_ = Column(BigInteger)

def get_session():
    seesion = ""
    return seesion
def get_result(session, id_list):
    query = session.query(MpLog27516.messageid_, MpLog27516.actiontype_, func.count().label('qv')). \
        filter(MpLog27516.messageid_.in_(id_list)). \
        group_by(MpLog27516.messageid_, MpLog27516.actiontype_)
    # 获取查询结果并添加到结果字典
    result_dict = {}
    if query is None:
        return result_dict
    for result in query:
        result_dict[result.messageid_] = [result.qv, result.messageid_, result.actiontype_]
    logger.info("UpdateMesssageData result_dict = %s " % result_dict)
    return result_dict


def UpdateMesssageData(mp_configs):
    session = get_session()
    id_list = []
    for ins in mp_configs:
        id_list.append(ins.id)
    result_dict = get_result(session, id_list)
    for ins in mp_configs:
        row = result_dict.get(ins.id)
        if row is None:
            continue
        if not row or len(row) != 3:
            continue
        if row[2] == "20000":
            ins.export_num = int(row[0])
        if row[2] == "30000":
            ins.clk_num = int(row[0])