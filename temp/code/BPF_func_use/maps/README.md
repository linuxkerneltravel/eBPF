#### 映射(map)

eBPF程序使用的主要数据结构是eBPF map，eBPF map是一种通用数据结构，它允许在内核内或内核与用户空间之间来回传递数据。顾名思义，“map(地图)”使用键存储和检索数据。

映射的maps是BPF数据保存，高级对象表,哈希表和直方图的基础。

1. BPF_TABLE

   - 语法：BPF_TABLE(_table_type, _key_type, _leaf_type, _name, _max_entries)

     创建一个映射，名字为name。大多数时候会被高层宏使用，例如BPF_HASH，BPF_HIST等。还有map.lookup()，map.lookup_or_init()，map.delete()，map.update()，map.insert()，map.increment()。

2. BPF_HASH

   - 语法：BPF_HASH(name, [key_type], [leaf_type], [size])

     创建一个name哈希表，中括号中是可选参数。

     默认：BPF_HASH(name, key_type = u64, leaf_type = u64, size = 10240)

     相关函数：map.lookup()，map.update()，map.increment()。

     整列中数据是预分配的，不能删除，所以没有删除操作。

3. BPF_HISTOGRAM

   - 语法：BPF_HISTOGRAM(name, [key_type], [size])

     创建一个直方图，默认是由64位整型桶索引。

4. map.lookup

   - 语法：*val map.lookup(&key)

     寻找map中键为key的值，如果存在则返回指向该键值的指针。

5. map.loopup_or_init

   - 语法：*val map.lookup_or_init(&key, &zero)

     在map中寻找键，找到返回键值的指针，找不到则初始化为第二个参数。

6. map.delete

   - 从map中删除某个键值。

7. map.update

   - 语法：map.update(&key, &val)

     更新键值。

8. map.insert

   - 插入键值

9. map.increment

   - 增加指定键的值，用于直方图。
