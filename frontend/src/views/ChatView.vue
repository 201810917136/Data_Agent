<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>AI 问数 - 二手车拍卖数据分析</h2>
    </div>
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="msg in chatStore.messages" :key="msg.id" class="message" :class="msg.role">
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
          <div v-if="msg.loading" class="loading">思考中...</div>
          <div v-if="msg.error && !msg.isPreview" class="error">{{ msg.error }}</div>

          <!-- 预览模式：展示生成逻辑 -->
          <div v-if="msg.isPreview && !msg.loading" class="preview-card">
            <div v-if="msg.questionUnderstanding" class="preview-section">
              <span class="label">问题理解：</span>
              <span>{{ msg.questionUnderstanding }}</span>
            </div>
            <div v-if="msg.tablesInvolved" class="preview-section">
              <span class="label">涉及表：</span>
              <span>{{ msg.tablesInvolved }}</span>
            </div>
            <div v-if="msg.queryLogic" class="preview-section">
              <span class="label">查询逻辑：</span>
              <span>{{ msg.queryLogic }}</span>
            </div>

            <!-- SQL 展示与编辑 -->
            <div class="sql-preview">
              <div class="sql-header">
                <span>生成的 SQL</span>
                <span v-if="msg.sqlValid" class="valid-badge">校验通过</span>
                <span v-else class="invalid-badge">校验失败</span>
              </div>
              <textarea
                v-if="msg.editing"
                v-model="msg.tempSql"
                class="sql-textarea"
                rows="6"
              ></textarea>
              <pre v-else><code>{{ msg.sql }}</code></pre>

              <!-- 操作按钮 -->
              <div class="sql-actions">
                <button
                  v-if="!msg.editing"
                  class="btn-edit"
                  @click="msg.editing = true; msg.tempSql = msg.sql"
                >编辑 SQL</button>
                <template v-else>
                  <button class="btn-confirm" @click="handleConfirm(msg)">确认执行</button>
                  <button class="btn-cancel" @click="msg.editing = false; msg.tempSql = undefined">取消</button>
                </template>
              </div>
            </div>
          </div>

          <!-- 普通模式：展示 SQL（可折叠） -->
          <div v-if="msg.sql && !msg.isPreview" class="sql-block">
            <details>
              <summary>查看 SQL</summary>
              <pre><code>{{ msg.sql }}</code></pre>
            </details>
          </div>

          <!-- 结果表格 -->
          <div v-if="msg.data && msg.data.length > 0" class="result-table">
            <el-table :data="msg.data" stripe border size="small" max-height="400">
              <el-table-column v-for="(val, key) in msg.data[0]" :key="key" :prop="key" :label="key" />
            </el-table>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="inputText"
        placeholder="输入你的问题，例如：昨日各门店销售额"
        @keyup.enter="handleSend"
        :disabled="isSending"
      >
        <template #append>
          <el-button type="primary" @click="handleSend" :loading="isSending">发送</el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const inputText = ref('')
const isSending = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

async function handleSend() {
  if (!inputText.value.trim()) return
  const question = inputText.value.trim()
  inputText.value = ''
  isSending.value = true
  await chatStore.sendPreview(question)
  isSending.value = false
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handleConfirm(msg: any) {
  if (!msg.tempSql && !msg.sql) return
  const sql = msg.tempSql || msg.sql
  chatStore.sendExecute(msg.content, sql)
  msg.editing = false
  msg.tempSql = undefined
}

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: 100vh; }
.chat-header { padding: 16px 24px; border-bottom: 1px solid #e4e7ed; background: #fff; }
.chat-header h2 { margin: 0; font-size: 18px; color: #303133; }
.chat-messages { flex: 1; overflow-y: auto; padding: 24px; background: #f5f7fa; }
.message { margin-bottom: 16px; display: flex; }
.message.user { justify-content: flex-end; }
.message-bubble { max-width: 70%; padding: 12px 16px; border-radius: 12px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.message.user .message-bubble { background: #409eff; color: #fff; }
.sql-block { margin-top: 8px; }
.sql-block pre { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 12px; }
.error { color: #f56c6c; margin-top: 8px; }
.result-table { margin-top: 12px; }
.chat-input { padding: 16px 24px; border-top: 1px solid #e4e7ed; background: #fff; }

/* 预览卡片样式 */
.preview-card {
  margin-top: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 12px 16px;
  background: #fafafa;
}
.preview-section {
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.6;
}
.preview-section .label {
  font-weight: 600;
  color: #409eff;
  margin-right: 4px;
}
.sql-preview {
  margin-top: 12px;
  border-top: 1px dashed #e4e7ed;
  padding-top: 12px;
}
.sql-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
}
.sql-header pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
.sql-textarea {
  width: 100%;
  font-family: monospace;
  font-size: 12px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  background: #fff;
}
.sql-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.btn-confirm {
  padding: 6px 16px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.btn-confirm:hover { background: #66b1ff; }
.btn-edit {
  padding: 6px 16px;
  background: #fff;
  color: #409eff;
  border: 1px solid #409eff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.btn-edit:hover { background: #ecf5ff; }
.btn-cancel {
  padding: 6px 16px;
  background: #fff;
  color: #909399;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.valid-badge {
  color: #67c23a;
  font-size: 12px;
  background: #f0f9eb;
  padding: 2px 8px;
  border-radius: 10px;
}
.invalid-badge {
  color: #f56c6c;
  font-size: 12px;
  background: #fef0f0;
  padding: 2px 8px;
  border-radius: 10px;
}
</style>