import { OpenFgaClient } from '@openfga/sdk';

/**
 * 初始化 OpenFGA 客户端
 *
 * 重要：OpenFgaClient 应该只初始化一次并在整个应用中复用
 * 这样可以：
 * 1. 避免重复初始化的开销
 * 2. 充分利用连接池
 * 3. 提高性能
 */
const fgaClient = new OpenFgaClient({
  apiUrl: process.env.FGA_API_URL || 'http://localhost:8080',
  storeId: process.env.FGA_STORE_ID,
  authorizationModelId: process.env.FGA_AUTHORIZATION_MODEL_ID,
});

/**
 * 检查用户是否有特定权限
 *
 * @param userId - 用户 ID
 * @param relation - 关系类型（owner, editor, viewer）
 * @param objectId - 对象 ID
 * @returns 是否有权限
 */
export async function checkPermission(
  userId: string,
  relation: string,
  objectId: string
): Promise<boolean> {
  try {
    const result = await fgaClient.check({
      user: `user:${userId}`,
      relation: relation,
      object: objectId,
    });

    return result.allowed;
  } catch (error) {
    console.error('OpenFGA check error:', error);
    throw new Error('权限检查失败');
  }
}

/**
 * 创建关系元组
 * 例如：将用户设置为文档的所有者
 *
 * @param userId - 用户 ID
 * @param relation - 关系类型
 * @param objectId - 对象 ID
 */
export async function createRelationship(
  userId: string,
  relation: string,
  objectId: string
): Promise<void> {
  try {
    await fgaClient.write({
      writes: [
        {
          user: `user:${userId}`,
          relation: relation,
          object: objectId,
        },
      ],
    });
  } catch (error) {
    console.error('OpenFGA write error:', error);
    throw new Error('创建权限关系失败');
  }
}

/**
 * 删除关系元组
 *
 * @param userId - 用户 ID
 * @param relation - 关系类型
 * @param objectId - 对象 ID
 */
export async function deleteRelationship(
  userId: string,
  relation: string,
  objectId: string
): Promise<void> {
  try {
    await fgaClient.write({
      deletes: [
        {
          user: `user:${userId}`,
          relation: relation,
          object: objectId,
        },
      ],
    });
  } catch (error) {
    console.error('OpenFGA delete error:', error);
    throw new Error('删除权限关系失败');
  }
}

/**
 * 列出用户有特定权限的所有对象
 *
 * @param userId - 用户 ID
 * @param relation - 关系类型
 * @param objectType - 对象类型
 * @returns 对象 ID 列表
 */
export async function listObjects(
  userId: string,
  relation: string,
  objectType: string
): Promise<string[]> {
  try {
    const result = await fgaClient.listObjects({
      user: `user:${userId}`,
      relation: relation,
      type: objectType,
    });

    return result.objects || [];
  } catch (error) {
    console.error('OpenFGA listObjects error:', error);
    throw new Error('获取对象列表失败');
  }
}

export { fgaClient };
