// =============================================================================
//  dary_heap.hpp  --  d 叉最大堆（d-ary max-heap）
//  对应《算法导论》第三版 第 6 章「堆排序」 + 思考题 6-2「对 d 叉堆的分析」
//
//  记号约定（与课堂讲义 02-1 高级数据结构-堆.pdf 一致）：
//    * 数组采用 1 起始下标：堆元素存放在 A[1..heap_size]，A[0] 作为哨兵不使用；
//    * 最大堆性质：A[PARENT(i)] >= A[i]；
//    * 讲义中的 ki >= k┊i/2┘ 是 d = 2 的特例，本文件把 PARENT 推广到一般 d。
//
//  本题（6-2）特别假设：维护「对象 -> 堆元素」的映射每次只需 O(1) 时间。
//  本实现用 pos_[id] = 数组下标 的形式兑现这一假设，供 INCREASE-KEY / DELETE
//  之类的「按对象定位」操作使用。
// =============================================================================
#ifndef DARY_HEAP_HPP
#define DARY_HEAP_HPP

#include <vector>
#include <stdexcept>
#include <string>
#include <limits>
#include <sstream>

namespace clrs {

// -----------------------------------------------------------------------------
//  可选：关键字比较次数计数器。
//  用 -DDARY_HEAP_COUNT 编译时启用，用于「复杂度实测」——直接数出每个操作
//  执行了多少次关键字比较，比墙钟时间更干净地验证 O(d log_d n) 这一结论。
//  正常使用时该宏展开为空，对性能零影响。
// -----------------------------------------------------------------------------
#ifdef DARY_HEAP_COUNT
inline unsigned long long g_cmp = 0;
#define DARY_CMP() (++g_cmp)
#else
#define DARY_CMP() ((void)0)
#endif

// 堆中存放的元素：关键字 key + 对象句柄 id。
// 真实场景里 id 可以是指向外部对象的指针/索引，这里用 int 代表。
struct Item {
    int key;
    int id;
};

class DaryMaxHeap {
public:
    // d 必须 >= 2；d = 2 即退化为《算法导论》里的二叉最大堆。
    explicit DaryMaxHeap(int d) : d_(d), size_(0) {
        if (d_ < 2)
            throw std::invalid_argument("DaryMaxHeap: d must be >= 2");
        a_.resize(2);          // a_[0] 哨兵，真正的堆从 a_[1] 开始
    }

    // ------------------------------------------------------------------
    //  6-2(a) 用数组表示 d 叉堆：三个下标公式
    // ------------------------------------------------------------------
    int d()      const { return d_; }
    int size()   const { return size_; }
    bool empty() const { return size_ == 0; }

    // 结点 i 的父结点下标（i = 1 为根，无父结点）
    int parent(int i) const {
        if (i <= 1) throw std::out_of_range("parent(1) does not exist");
        return (i - 2) / d_ + 1;            // = floor((i-2)/d) + 1
    }

    // 结点 i 的第 j 个孩子下标（1 <= j <= d）
    int child(int i, int j) const {
        if (j < 1 || j > d_) throw std::out_of_range("child index j out of 1..d");
        return d_ * (i - 1) + j + 1;        // = d(i-1) + j + 1
    }

    // 堆高（根到最深叶子的边数）。对紧凑存储的完全 d 叉堆等于
    //   floor( log_d( (n-1)(d-1) + 1 ) )
    // 这里用「从最后一个结点沿父链上溯」的方式计算，避免浮点误差。
    int height() const {
        int h = 0, i = size_;
        while (i > 1) { i = parent(i); ++h; }
        return h;
    }

    // 最后一个「内部结点」（即有孩子的结点）的下标：parent(n)
    int lastInternal() const {
        return size_ >= 2 ? parent(size_) : 0;
    }

    int lastChild(int i) const {           // i 的孩子中最大的下标（可能越界）
        return d_ * (i - 1) + d_ + 1;
    }

    // ------------------------------------------------------------------
    //  基本访问
    // ------------------------------------------------------------------
    const Item& top() const {
        ensureNotEmpty("top");
        return a_[1];
    }

    void clear() {
        for (int i = 1; i <= size_; ++i)
            if (a_[i].id >= 0 && a_[i].id < (int)pos_.size()) pos_[a_[i].id] = -1;
        size_ = 0;
    }

    // 对象 id 当前所在的下标（1 起始）；不存在返回 -1。
    int indexOf(int id) const {
        if (id < 0 || id >= (int)pos_.size()) return -1;
        return pos_[id];
    }

    // ------------------------------------------------------------------
    //  6-2(c) 的配套过程：MAX-HEAPIFY（下沉）
    //  每层最多比较 d 个孩子 —— 这是 d 叉堆与二叉堆最本质的差别。
    //  这里给出「迭代版」：把递归改写为循环，省掉函数调用开销，
    //  这也是后面「瓶颈与改进」中提到的第一条优化。
    // ------------------------------------------------------------------
    void maxHeapify(int i) {
        while (true) {
            int largest = i;
            int first = child(i, 1);
            int last  = std::min(lastChild(i), size_);
            for (int c = first; c <= last; ++c) {      // 顺序扫描 d 个孩子
                DARY_CMP();                            // 每比较一次记一次
                if (a_[c].key > a_[largest].key) largest = c;
            }
            if (largest == i) return;                  // 已满足堆性质，结束
            swapNodes(i, largest);
            i = largest;                               // 继续向下
        }
    }

    // 递归版（与讲义/教材伪码逐行对应，便于讲解，性能略差）
    void maxHeapifyRec(int i) {
        int largest = i;
        int first = child(i, 1);
        int last  = std::min(lastChild(i), size_);
        for (int c = first; c <= last; ++c)
            if (a_[c].key > a_[largest].key) largest = c;
        if (largest != i) {
            swapNodes(i, largest);
            maxHeapifyRec(largest);
        }
    }

    // ------------------------------------------------------------------
    //  建堆：Floyd 自底向上，O(n)
    // ------------------------------------------------------------------
    void build(const std::vector<Item>& items) {
        clear();
        a_.assign(1, Item{0, -1});                     // 哨兵
        a_.insert(a_.end(), items.begin(), items.end());
        size_ = (int)items.size();
        for (int i = 1; i <= size_; ++i) {
            int id = a_[i].id;
            if (id >= 0) {
                if ((int)pos_.size() <= id) pos_.resize(id + 1, -1);
                pos_[id] = i;
            }
        }
        for (int i = lastInternal(); i >= 1; --i) maxHeapify(i);
    }

    // ------------------------------------------------------------------
    //  6-2(c) EXTRACT-MAX：摘掉根，把最后一个元素搬到根再下沉
    //  运行时间 O(d log_d n)
    // ------------------------------------------------------------------
    Item extractMax() {
        ensureNotEmpty("extractMax");
        Item mx = a_[1];
        if (a_[1].id >= 0) pos_[a_[1].id] = -1;
        a_[1] = a_[size_];                             // 末元素补到根
        --size_;
        if (size_ >= 1) {
            if (a_[1].id >= 0) pos_[a_[1].id] = 1;
            maxHeapify(1);
        }
        return mx;
    }

    // ------------------------------------------------------------------
    //  6-2(d) INCREASE-KEY：把下标 i 的关键字增大到 key，然后上浮
    //  运行时间 O(log_d n)（每层 O(1)）
    // ------------------------------------------------------------------
    void increaseKey(int i, int key) {
        if (i < 1 || i > size_) throw std::out_of_range("increaseKey: i out of range");
        if (key < a_[i].key) throw std::invalid_argument("increaseKey: new key is smaller");
        a_[i].key = key;
        siftUp(i);
    }

    // 按对象句柄做 INCREASE-KEY（依赖 O(1) 的 pos 映射）
    void increaseKeyById(int id, int key) {
        int i = indexOf(id);
        if (i < 0) throw std::invalid_argument("increaseKeyById: unknown object");
        increaseKey(i, key);
    }

    // ------------------------------------------------------------------
    //  6-2(e) INSERT：尾部追加 -inf，再做一次 INCREASE-KEY
    //  运行时间 O(log_d n)
    // ------------------------------------------------------------------
    void insert(int key, int id = -1) {
        if (a_.size() <= (size_t)size_ + 1) a_.resize(size_ + 2);
        ++size_;
        a_[size_].key = std::numeric_limits<int>::min();   // 先放 -inf
        a_[size_].id  = id;
        if (id >= 0) {
            if ((int)pos_.size() <= id) pos_.resize(id + 1, -1);
            pos_[id] = size_;
        }
        increaseKey(size_, key);                            // 再上浮到正确位置
    }

    // ------------------------------------------------------------------
    //  校验 / 调试用
    // ------------------------------------------------------------------
    bool isMaxHeap() const {
        for (int i = 1; i <= size_; ++i) {
            int first = child(i, 1);
            int last  = std::min(lastChild(i), size_);
            for (int c = first; c <= last; ++c)
                if (a_[c].key > a_[i].key) return false;
        }
        return true;
    }

    // 以「层序」打印数组（含下标），便于讲 6-2(a) 的数组表示
    std::string toArrayString() const {
        std::ostringstream os;
        os << "[";
        for (int i = 1; i <= size_; ++i) {
            if (i > 1) os << ", ";
            os << a_[i].key;
        }
        os << "]";
        return os.str();
    }

    // 逐层打印，直观展示 d 叉堆的树形结构
    std::string toTreeString() const {
        std::ostringstream os;
        int i = 1, depth = 0;
        while (i <= size_) {
            os << "level " << depth << ": ";
            int cnt = 0, cap = 1;
            for (int k = 0; k < depth; ++k) cap *= d_;
            for (; cnt < cap && i <= size_; ++cnt, ++i) os << a_[i].key << " ";
            os << "\n";
            ++depth;
        }
        return os.str();
    }

    const std::vector<Item>& raw() const { return a_; }

private:
    void ensureNotEmpty(const char* who) const {
        if (size_ == 0) throw std::underflow_error(std::string(who) + ": heap underflow");
    }

    void swapNodes(int i, int j) {
        std::swap(a_[i], a_[j]);
        if (a_[i].id >= 0) pos_[a_[i].id] = i;
        if (a_[j].id >= 0) pos_[a_[j].id] = j;
    }

    // 从 i 沿父链上浮
    void siftUp(int i) {
        while (i > 1) {
            int p = parent(i);
            DARY_CMP();                                // 父 vs 子：一次比较
            if (a_[p].key >= a_[i].key) break;
            swapNodes(i, p);
            i = p;
        }
    }

    int d_;
    int size_;
    std::vector<Item> a_;      // a_[1..size_] 为堆
    std::vector<int>  pos_;    // 对象 id -> 下标（-1 表示不在堆中）
};

} // namespace clrs

#endif // DARY_HEAP_HPP
