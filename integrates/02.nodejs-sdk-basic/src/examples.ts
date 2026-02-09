import { OpenFGAClient } from './client';
import { randomUUID } from 'crypto';

/**
 * OpenFGA Node.js/TypeScript SDK 完整使用示例
 *
 * 本示例演示了如何使用 OpenFGA SDK 进行：
 * 1. 客户端初始化
 * 2. 写入和删除关系元组
 * 3. 权限检查
 * 4. 批量权限检查
 * 5. 列出对象和用户
 */

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(60));
  console.log('OpenFGA Node.js/TypeScript SDK 使用示例');
  console.log('='.repeat(60));
  console.log();

  try {
    // ========================================
    // 1. 初始化客户端
    // ========================================
    console.log('1. 初始化 OpenFGA 客户端');
    console.log('-'.repeat(60));

    const client = new OpenFGAClient({
      apiUrl: process.env.FGA_API_URL || 'http://localhost:8080',
      storeId: process.env.FGA_STORE_ID,
      authorizationModelId: process.env.FGA_MODEL_ID,
    });

    console.log();

    // ========================================
    // 2. 写入关系元组
    // ========================================
    console.log('2. 写入关系元组');
    console.log('-'.repeat(60));

    // 创建组织成员关系
    await client.writeTuples([
      {
        user: 'user:alice',
        relation: 'member',
        object: 'organization:acme',
      },
      {
        user: 'user:bob',
        relation: 'member',
        object: 'organization:acme',
      },
    ]);

    // 创建文档所有者关系
    await client.writeTuples([
      {
        user: 'user:alice',
        relation: 'owner',
        object: 'document:roadmap',
      },
    ]);

    // 创建文档查看者关系
    await client.writeTuples([
      {
        user: 'user:bob',
        relation: 'viewer',
        object: 'document:roadmap',
      },
      {
        user: 'organization:acme#member',
        relation: 'viewer',
        object: 'document:budget',
      },
    ]);

    // 创建文件夹关系
    await client.writeTuples([
      {
        user: 'user:alice',
        relation: 'owner',
        object: 'folder:product',
      },
      {
        user: 'folder:product',
        relation: 'parent',
        object: 'document:spec',
      },
    ]);

    console.log();

    // ========================================
    // 3. 权限检查
    // ========================================
    console.log('3. 权限检查');
    console.log('-'.repeat(60));

    // 检查 Alice 是否可以查看 roadmap 文档
    const aliceCanViewRoadmap = await client.check(
      'user:alice',
      'viewer',
      'document:roadmap'
    );
    console.log(`Alice 可以查看 roadmap 文档: ${aliceCanViewRoadmap}`);

    // 检查 Bob 是否可以查看 roadmap 文档
    const bobCanViewRoadmap = await client.check(
      'user:bob',
      'viewer',
      'document:roadmap'
    );
    console.log(`Bob 可以查看 roadmap 文档: ${bobCanViewRoadmap}`);

    // 检查 Bob 是否可以编辑 roadmap 文档
    const bobCanEditRoadmap = await client.check(
      'user:bob',
      'editor',
      'document:roadmap'
    );
    console.log(`Bob 可以编辑 roadmap 文档: ${bobCanEditRoadmap}`);

    // 检查 Alice 是否可以查看 budget 文档（通过组织成员关系）
    const aliceCanViewBudget = await client.check(
      'user:alice',
      'viewer',
      'document:budget'
    );
    console.log(`Alice 可以查看 budget 文档（通过组织成员）: ${aliceCanViewBudget}`);

    // 检查 Alice 是否可以查看 spec 文档（通过文件夹父级关系）
    const aliceCanViewSpec = await client.check(
      'user:alice',
      'viewer',
      'document:spec'
    );
    console.log(`Alice 可以查看 spec 文档（通过文件夹父级）: ${aliceCanViewSpec}`);

    console.log();

    // ========================================
    // 4. 批量权限检查
    // ========================================
    console.log('4. 批量权限检查');
    console.log('-'.repeat(60));

    const corrId1 = randomUUID();
    const corrId2 = randomUUID();

    const batchCheckResult = await client.batchCheck([
      {
        user: 'user:alice',
        relation: 'viewer',
        object: 'document:roadmap',
        correlationId: corrId1,
      },
      {
        user: 'user:alice',
        relation: 'viewer',
        object: 'document:budget',
        correlationId: corrId2,
      },
      {
        user: 'user:bob',
        relation: 'editor',
        object: 'document:roadmap',
      },
    ]);

    console.log('批量检查结果:');
    batchCheckResult.result?.forEach((item) => {
      console.log(
        `  - ${item.request?.user} ${item.allowed ? '可以' : '不可以'} ${item.request?.relation} ${item.request?.object}`
      );
      if (item.correlationId) {
        console.log(`    关联 ID: ${item.correlationId}`);
      }
    });

    console.log();

    // ========================================
    // 5. 列出对象
    // ========================================
    console.log('5. 列出用户可以访问的对象');
    console.log('-'.repeat(60));

    // 列出 Alice 可以查看的所有文档
    const aliceDocuments = await client.listObjects(
      'user:alice',
      'viewer',
      'document'
    );
    console.log(`Alice 可以查看的文档: ${aliceDocuments.join(', ')}`);

    // 列出 Bob 可以查看的所有文档
    const bobDocuments = await client.listObjects(
      'user:bob',
      'viewer',
      'document'
    );
    console.log(`Bob 可以查看的文档: ${bobDocuments.join(', ')}`);

    // 使用上下文元组列出对象
    const aliceDocumentsWithContext = await client.listObjects(
      'user:alice',
      'viewer',
      'document',
      [
        {
          user: 'user:alice',
          relation: 'editor',
          object: 'document:proposal',
        },
      ]
    );
    console.log(
      `Alice 可以查看的文档（包含上下文）: ${aliceDocumentsWithContext.join(', ')}`
    );

    console.log();

    // ========================================
    // 6. 列出用户
    // ========================================
    console.log('6. 列出可以访问对象的用户');
    console.log('-'.repeat(60));

    // 列出可以查看 roadmap 文档的用户
    const roadmapViewers = await client.listUsers(
      'document',
      'roadmap',
      'viewer',
      [{ type: 'user' }]
    );

    console.log('可以查看 roadmap 文档的用户:');
    roadmapViewers.users?.forEach((user) => {
      if (user.object) {
        console.log(`  - ${user.object.type}:${user.object.id}`);
      } else if (user.userset) {
        console.log(`  - ${user.userset.type} (用户集)`);
      }
    });

    console.log();

    // ========================================
    // 7. 读取关系元组
    // ========================================
    console.log('7. 读取关系元组');
    console.log('-'.repeat(60));

    // 读取所有与 Alice 相关的关系元组
    const aliceTuples = await client.readTuples({
      user: 'user:alice',
    });

    console.log('Alice 相关的关系元组:');
    aliceTuples.tuples?.forEach((tuple) => {
      console.log(
        `  - ${tuple.key.user} ${tuple.key.relation} ${tuple.key.object}`
      );
    });

    // 读取所有 roadmap 文档的关系元组
    const roadmapTuples = await client.readTuples({
      object: 'document:roadmap',
    });

    console.log('\nroadmap 文档的关系元组:');
    roadmapTuples.tuples?.forEach((tuple) => {
      console.log(
        `  - ${tuple.key.user} ${tuple.key.relation} ${tuple.key.object}`
      );
    });

    console.log();

    // ========================================
    // 8. 同时写入和删除关系元组
    // ========================================
    console.log('8. 同时写入和删除关系元组（事务模式）');
    console.log('-'.repeat(60));

    // 将 Bob 从 viewer 升级为 editor
    await client.writeAndDeleteTuples(
      [
        {
          user: 'user:bob',
          relation: 'editor',
          object: 'document:roadmap',
        },
      ],
      [
        {
          user: 'user:bob',
          relation: 'viewer',
          object: 'document:roadmap',
        },
      ]
    );

    // 验证更改
    const bobCanEditAfterUpgrade = await client.check(
      'user:bob',
      'editor',
      'document:roadmap'
    );
    console.log(`Bob 现在可以编辑 roadmap 文档: ${bobCanEditAfterUpgrade}`);

    console.log();

    // ========================================
    // 9. 删除关系元组
    // ========================================
    console.log('9. 删除关系元组');
    console.log('-'.repeat(60));

    // 删除 Bob 的编辑权限
    await client.deleteTuples([
      {
        user: 'user:bob',
        relation: 'editor',
        object: 'document:roadmap',
      },
    ]);

    // 验证删除
    const bobCanEditAfterDelete = await client.check(
      'user:bob',
      'editor',
      'document:roadmap'
    );
    console.log(`Bob 删除权限后可以编辑 roadmap 文档: ${bobCanEditAfterDelete}`);

    console.log();

    // ========================================
    // 10. 错误处理示例
    // ========================================
    console.log('10. 错误处理示例');
    console.log('-'.repeat(60));

    try {
      // 尝试检查不存在的关系
      await client.check('user:charlie', 'invalid_relation', 'document:test');
    } catch (error) {
      console.log('捕获到预期的错误:');
      console.log(`  错误信息: ${error instanceof Error ? error.message : String(error)}`);
    }

    console.log();

    // ========================================
    // 完成
    // ========================================
    console.log('='.repeat(60));
    console.log('示例执行完成！');
    console.log('='.repeat(60));
  } catch (error) {
    console.error('执行过程中发生错误:');
    console.error(error);
    process.exit(1);
  }
}

// 运行主函数
if (require.main === module) {
  main().catch((error) => {
    console.error('未捕获的错误:', error);
    process.exit(1);
  });
}

export { main };
