<template>
  <div ref="chartContainer" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import * as echarts from 'echarts';

// 定义该组件期望接收的props
const props = defineProps({
  nodes: Array,
  links: Array,
  categories: Array
});

// 创建一个DOM元素的引用，ECharts将在这个DOM上初始化
const chartContainer = ref(null);
let myChart = null;

// 获取所有属性的函数（包括所有信息）
const getAllProperties = (data) => {
  const excludeKeys = ['symbolSize', '_internal_id', '_relationship_id', '_start_node_id', '_end_node_id']; // 排除技术性字段
  const allProps = {};
  for (const [key, value] of Object.entries(data)) {
    if (!excludeKeys.includes(key) && value !== null && value !== undefined && value !== '') {
      allProps[key] = value;
    }
  }
  return allProps;
};

// 格式化属性名的函数
const formatPropertyName = (key) => {
  const nameMap = {
    'id': 'ID',
    'name': '名称',
    'category': '类型',
    'labels': '标签',
    'source': '从',
    'target': '到',
    'type': '关系类型',
    'degree': '学位',
    'major': '专业',
    'year': '年份',
    'title': '标题',
    'author': '作者',
    'publication': '发表',
    'department': '部门',
    'position': '职位',
    'age': '年龄',
    'email': '邮箱',
    'phone': '电话',
    'gender': '性别'
  };
  return nameMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// 格式化值的函数
const formatValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否';
  }
  return String(value);
};

// 生成详细tooltip内容的函数
const generateTooltipContent = (data, title) => {
  const properties = getAllProperties(data);
  let content = `<div style="max-width: 300px; line-height: 1.5;">`;
  content += `<div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #333;">${title}</div>`;
  
  for (const [key, value] of Object.entries(properties)) {
    const label = formatPropertyName(key);
    const formattedValue = formatValue(value);
    content += `<div style="margin-bottom: 4px; display: flex; justify-content: space-between;">`;
    content += `<span style="color: #666; margin-right: 10px;">${label}:</span>`;
    content += `<span style="color: #333; font-weight: 500;">${formattedValue}</span>`;
    content += `</div>`;
  }
  
  content += `</div>`;
  return content;
};

// ECharts的配置项
const option = {
  tooltip: {
    // 自定义tooltip显示内容
    formatter: function (params) {
      if (params.dataType === 'node') {
        return generateTooltipContent(params.data, `节点: ${params.data.name}`);
      } else if (params.dataType === 'edge') {
        return generateTooltipContent(params.data, `关系: ${params.data.name}`);
      }
    },
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#ddd',
    borderWidth: 1,
    textStyle: {
      color: '#333'
    }
  },
  legend: {
    data: props.categories.map(a => a.name)
  },
  series: [
    {
      type: 'graph',
      layout: 'force',
      roam: true, // 开启鼠标缩放和拖拽
      draggable: true, // 开启节点拖拽
      label: {
        show: true,
        position: 'right'
      },
      edgeLabel: {
        show: true, // 显示边上的标签
        fontSize: 12,
        color: '#666',
        formatter: function (params) {
          return params.data.name; // 显示关系名称而不是source-target
        }
      },
      force: {
        repulsion: 600, // 增加节点间的斥力，让连线更长
        edgeLength: 250, // 设置边的理想长度
        layoutAnimation: true // 开启布局动画
      },
      lineStyle: {
        color: '#999',
        width: 2,
        curveness: 0 // 给连线添加一点弯曲度，更美观
      },
      edgeSymbol: ['none', 'arrow'], // 设置连线两端的符号：起点无符号，终点为箭头
      edgeSymbolSize: [0, 10], // 设置符号大小：起点0，箭头大小10
      emphasis: {
        focus: 'adjacency', // 高亮相邻节点和连线
        lineStyle: {
          width: 4
        }
      },
      // 关键数据
      data: props.nodes,
      links: props.links,
      categories: props.categories,
    }
  ]
};

// onMounted是Vue的生命周期钩子，在组件挂载到页面后执行
onMounted(async () => {
  await nextTick(); // 确保DOM已经渲染
  myChart = echarts.init(chartContainer.value);
  myChart.setOption(option);
  
  // 添加窗口resize事件监听
  const handleResize = () => {
    if (myChart) {
      myChart.resize();
    }
  };
  
  window.addEventListener('resize', handleResize);
  
  // 在组件卸载时清理
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (myChart) {
      myChart.dispose();
    }
  });
});

// 使用watch来监听props的变化，如果数据更新了，图表也需要更新
watch(() => [props.nodes, props.links], (newVal) => {
  if (myChart) {
    myChart.setOption({
      series: [{
        data: newVal[0],
        links: newVal[1],
        // 确保更新时保持所有配置
        draggable: true,
        edgeLabel: {
          show: true,
          fontSize: 12,
          color: '#666',
          formatter: function (params) {
            return params.data.name; // 显示关系名称而不是source-target
          }
        },
        force: {
          repulsion: 300,
          edgeLength: 150,
          layoutAnimation: true
        },
        lineStyle: {
          color: '#999',
          width: 2,
          curveness: 0.005
        },
        edgeSymbol: ['none', 'arrow'], // 箭头配置
        edgeSymbolSize: [0, 10], // 箭头大小
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          }
        }
      }]
    });
    // 数据更新后重新调整大小
    setTimeout(() => {
      if (myChart) {
        myChart.resize();
      }
    }, 100);
  }
});
</script>

<style scoped>
/* 图表容器样式 */
div[ref="chartContainer"] {
  display: block;
  width: 100% !important;
  height: 100% !important;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-sizing: border-box;
}
</style>