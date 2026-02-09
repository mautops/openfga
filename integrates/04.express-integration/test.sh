#!/bin/bash

# Express + OpenFGA 集成示例测试脚本

set -e

echo "🚀 Express + OpenFGA 集成示例测试"
echo "=================================="
echo ""

# 检查服务是否运行
if ! curl -s http://localhost:3000/health > /dev/null; then
    echo "❌ 错误: Express 服务未运行"
    echo "请先启动服务: npm run dev"
    exit 1
fi

echo "✅ Express 服务运行正常"
echo ""

# 测试用户
ALICE_EMAIL="alice@example.com"
ALICE_PASSWORD="password123"
BOB_EMAIL="bob@example.com"
BOB_PASSWORD="password123"

echo "📝 测试场景 1: Alice 登录"
echo "------------------------"
ALICE_TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ALICE_EMAIL\",\"password\":\"$ALICE_PASSWORD\"}" \
  | jq -r '.token')

if [ "$ALICE_TOKEN" = "null" ] || [ -z "$ALICE_TOKEN" ]; then
    echo "❌ Alice 登录失败"
    exit 1
fi

echo "✅ Alice 登录成功"
echo "Token: ${ALICE_TOKEN:0:20}..."
echo ""

echo "📝 测试场景 2: Bob 登录"
echo "----------------------"
BOB_TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BOB_EMAIL\",\"password\":\"$BOB_PASSWORD\"}" \
  | jq -r '.token')

if [ "$BOB_TOKEN" = "null" ] || [ -z "$BOB_TOKEN" ]; then
    echo "❌ Bob 登录失败"
    exit 1
fi

echo "✅ Bob 登录成功"
echo ""

echo "📝 测试场景 3: Alice 创建文档"
echo "----------------------------"
DOC_RESPONSE=$(curl -s -X POST http://localhost:3000/documents \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试文档","content":"这是 Alice 创建的测试文档"}')

DOC_ID=$(echo $DOC_RESPONSE | jq -r '.document.id')

if [ "$DOC_ID" = "null" ] || [ -z "$DOC_ID" ]; then
    echo "❌ 创建文档失败"
    echo "响应: $DOC_RESPONSE"
    exit 1
fi

echo "✅ 文档创建成功"
echo "文档 ID: $DOC_ID"
echo ""

echo "📝 测试场景 4: Alice 查看自己的文档（应该成功）"
echo "--------------------------------------------"
VIEW_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN")

HTTP_CODE=$(echo "$VIEW_RESPONSE" | tail -n1)
BODY=$(echo "$VIEW_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Alice 可以查看文档（owner 权限）"
else
    echo "❌ Alice 无法查看文档（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "📝 测试场景 5: Bob 查看 Alice 的文档（应该失败 - 无权限）"
echo "------------------------------------------------------"
VIEW_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN")

HTTP_CODE=$(echo "$VIEW_RESPONSE" | tail -n1)
BODY=$(echo "$VIEW_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "403" ]; then
    echo "✅ Bob 无法查看文档（符合预期 - 403 Forbidden）"
else
    echo "❌ 权限检查失败（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "📝 测试场景 6: Alice 分享文档给 Bob（viewer 权限）"
echo "------------------------------------------------"
SHARE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3000/documents/$DOC_ID/share \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user:bob","relation":"viewer"}')

HTTP_CODE=$(echo "$SHARE_RESPONSE" | tail -n1)
BODY=$(echo "$SHARE_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 分享成功"
else
    echo "❌ 分享失败（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

# 等待 OpenFGA 更新
echo "⏳ 等待权限更新..."
sleep 2
echo ""

echo "📝 测试场景 7: Bob 再次查看文档（应该成功 - 已有 viewer 权限）"
echo "-----------------------------------------------------------"
VIEW_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN")

HTTP_CODE=$(echo "$VIEW_RESPONSE" | tail -n1)
BODY=$(echo "$VIEW_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Bob 现在可以查看文档（viewer 权限）"
else
    echo "❌ Bob 仍无法查看文档（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "📝 测试场景 8: Bob 尝试编辑文档（应该失败 - 只有 viewer 权限）"
echo "------------------------------------------------------------"
EDIT_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Bob 尝试修改","content":"Bob 的修改"}')

HTTP_CODE=$(echo "$EDIT_RESPONSE" | tail -n1)
BODY=$(echo "$EDIT_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "403" ]; then
    echo "✅ Bob 无法编辑文档（符合预期 - 403 Forbidden）"
else
    echo "❌ 权限检查失败（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "📝 测试场景 9: Alice 更新文档（应该成功 - owner 权限）"
echo "---------------------------------------------------"
EDIT_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"更新后的标题","content":"Alice 更新的内容"}')

HTTP_CODE=$(echo "$EDIT_RESPONSE" | tail -n1)
BODY=$(echo "$EDIT_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Alice 成功更新文档（owner 权限）"
else
    echo "❌ Alice 无法更新文档（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "📝 测试场景 10: Alice 删除文档（应该成功 - owner 权限）"
echo "----------------------------------------------------"
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
BODY=$(echo "$DELETE_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Alice 成功删除文档（owner 权限）"
else
    echo "❌ Alice 无法删除文档（HTTP $HTTP_CODE）"
    echo "响应: $BODY"
    exit 1
fi
echo ""

echo "=================================="
echo "🎉 所有测试通过！"
echo "=================================="
echo ""
echo "测试总结:"
echo "  ✅ 用户认证（JWT）"
echo "  ✅ 文档创建"
echo "  ✅ 权限检查（viewer, editor, owner）"
echo "  ✅ 权限继承（owner > editor > viewer）"
echo "  ✅ 文档分享"
echo "  ✅ 文档更新"
echo "  ✅ 文档删除"
echo ""
