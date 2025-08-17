# app/services/graph_service.py
# backend/app/services/graph_service.py
from neo4j import GraphDatabase, Driver

class GraphService:
    def __init__(self, driver: Driver):
        self.driver = driver

    def get_node_count(self) -> int:
        # ... (此函数保持不变) ...
        try:
            records, _, _ = self.driver.execute_query("MATCH (n) RETURN count(n) AS node_count")
            return records[0]["node_count"] if records else 0
        except Exception as e:
            print(f"Error in get_node_count: {e}")
            return -1

    def get_graph_for_echarts(self, node_limit: int = 25) -> dict:
        """
        查询图数据并转换为ECharts所需的格式。
        """
        print(f"正在查询最多 {node_limit} 个节点及其关系...")
        
        nodes_dict = {}
        links_list = []
        categories_set = set()

        try:
            # 首先获取所有节点（包括孤立节点）
            nodes_query = """
            MATCH (n)
            RETURN n
            LIMIT $limit
            """
            node_records, _, _ = self.driver.execute_query(nodes_query, limit=node_limit)
            
            # 处理所有节点
            node_name_to_id = {}  # 用于存储节点名称到内部ID的映射
            for record in node_records:
                node = record["n"]
                node_id = node.element_id
                node_name = node.get("name", f"Node_{node_id[-8:]}")  # 使用name或ID后8位作为显示名称
                label = list(node.labels)[0] if node.labels else "Unknown"
                categories_set.add(label)
                
                # 存储映射关系
                node_name_to_id[node_id] = node_name
                
                # 构建节点数据，包含所有属性
                node_data = {
                    "id": node_name,  # 使用可读名称作为ECharts的id
                    "name": node_name,
                    "category": label,
                    "symbolSize": 40 if label == "Scholar" else 30
                }
                
                # 添加节点的所有属性
                for key, value in node.items():
                    if key not in node_data:  # 避免覆盖已有的字段
                        node_data[key] = value
                
                # 添加节点的标签信息
                node_data["labels"] = list(node.labels)
                
                # 添加内部ID供调试使用
                node_data["_internal_id"] = node_id
                
                nodes_dict[node_id] = node_data
            
            # 然后获取这些节点之间的关系
            relations_query = """
            MATCH (n)-[r]-(m)
            WHERE elementId(n) IN $node_ids AND elementId(m) IN $node_ids
            RETURN n, r, m
            """
            node_ids = list(nodes_dict.keys())
            relation_records, _, _ = self.driver.execute_query(relations_query, node_ids=node_ids)

            
            # 处理关系
            processed_rel_ids = set()
            for record in relation_records:
                source_node = record["n"]
                target_node = record["m"]
                relationship = record["r"]
                
                # 避免重复添加同一个关系
                if relationship.element_id not in processed_rel_ids:
                    # 获取节点的可读名称
                    source_name = node_name_to_id.get(source_node.element_id, source_node.element_id)
                    target_name = node_name_to_id.get(target_node.element_id, target_node.element_id)
                    
                    # 构建关系数据，包含所有属性
                    link_data = {
                        "source": source_name,  # 使用可读名称
                        "target": target_name,  # 使用可读名称
                        "name": relationship.type,
                        "type": relationship.type  # 关系类型
                    }
                    
                    # 添加关系的所有属性
                    for key, value in relationship.items():
                        if key not in link_data:  # 避免覆盖已有的字段
                            link_data[key] = value
                    
                    # 添加关系的内部信息
                    link_data["_relationship_id"] = relationship.element_id
                    link_data["_start_node_id"] = relationship.start_node.element_id
                    link_data["_end_node_id"] = relationship.end_node.element_id
                    
                    links_list.append(link_data)
                    processed_rel_ids.add(relationship.element_id)

            # 构建最终数据
            final_data = {
                "nodes": list(nodes_dict.values()),
                "links": links_list,
                "categories": [{"name": cat} for cat in sorted(list(categories_set))]
            }

            print(f"查询到 {len(final_data['nodes'])} 个节点, {len(final_data['links'])} 个关系")
            
            # 调试信息：显示第一个节点的所有属性
            if final_data['nodes']:
                print(f"示例节点属性: {list(final_data['nodes'][0].keys())}")
            
            # 调试信息：显示第一个关系的所有属性
            if final_data['links']:
                print(f"示例关系属性: {list(final_data['links'][0].keys())}")
                
            return final_data

        except Exception as e:
            print(f"Error in get_graph_for_echarts: {e}")
            return {"nodes": [], "links": [], "categories": []}