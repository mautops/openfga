import { OpenFGAClient, RelationshipTuple } from './client';

/**
 * OpenFGA 高级使用场景示例
 *
 * 本文件展示了更多实际应用场景：
 * 1. 多租户权限管理
 * 2. 角色继承
 * 3. 动态权限检查
 * 4. 权限审计
 */

/**
 * 场景 1: 多租户文档管理系统
 */
export class MultiTenantDocumentSystem {
  constructor(private client: OpenFGAClient) {}

  /**
   * 为租户创建文档并设置权限
   */
  async createDocument(
    tenantId: string,
    documentId: string,
    ownerId: string,
    viewerIds: string[] = [],
    editorIds: string[] = []
  ): Promise<void> {
    const tuples: RelationshipTuple[] = [
      // 设置文档所有者
      {
        user: `user:${ownerId}`,
        relation: 'owner',
        object: `document:${documentId}`,
      },
      // 设置文档所属租户
      {
        user: `organization:${tenantId}#member`,
        relation: 'viewer',
        object: `document:${documentId}`,
      },
    ];

    // 添加查看者
    viewerIds.forEach((viewerId) => {
      tuples.push({
        user: `user:${viewerId}`,
        relation: 'viewer',
        object: `document:${documentId}`,
      });
    });

    // 添加编辑者
    editorIds.forEach((editorId) => {
      tuples.push({
        user: `user:${editorId}`,
        relation: 'editor',
        object: `document:${documentId}`,
      });
    });

    await this.client.writeTuples(tuples);
    console.log(`文档 ${documentId} 已创建，所有者: ${ownerId}`);
  }

  /**
   * 检查用户是否可以访问文档
   */
  async canAccessDocument(
    userId: string,
    documentId: string,
    action: 'viewer' | 'editor' | 'deleter'
  ): Promise<boolean> {
    return await this.client.check(
      `user:${userId}`,
      action,
      `document:${documentId}`
    );
  }

  /**
   * 获取用户可以访问的所有文档
   */
  async getUserDocuments(
    userId: string,
    action: 'viewer' | 'editor' = 'viewer'
  ): Promise<string[]> {
    const documents = await this.client.listObjects(
      `user:${userId}`,
      action,
      'document'
    );

    // 提取文档 ID
    return documents.map((doc) => doc.replace('document:', ''));
  }

  /**
   * 转移文档所有权
   */
  async transferOwnership(
    documentId: string,
    oldOwnerId: string,
    newOwnerId: string
  ): Promise<void> {
    await this.client.writeAndDeleteTuples(
      [
        {
          user: `user:${newOwnerId}`,
          relation: 'owner',
          object: `document:${documentId}`,
        },
      ],
      [
        {
          user: `user:${oldOwnerId}`,
          relation: 'owner',
          object: `document:${documentId}`,
        },
      ]
    );

    console.log(`文档 ${documentId} 所有权已从 ${oldOwnerId} 转移到 ${newOwnerId}`);
  }

  /**
   * 共享文档给用户
   */
  async shareDocument(
    documentId: string,
    userIds: string[],
    permission: 'viewer' | 'editor'
  ): Promise<void> {
    const tuples: RelationshipTuple[] = userIds.map((userId) => ({
      user: `user:${userId}`,
      relation: permission,
      object: `document:${documentId}`,
    }));

    await this.client.writeTuples(tuples);
    console.log(`文档 ${documentId} 已共享给 ${userIds.length} 个用户`);
  }

  /**
   * 取消文档共享
   */
  async unshareDocument(
    documentId: string,
    userIds: string[],
    permission: 'viewer' | 'editor'
  ): Promise<void> {
    const tuples: RelationshipTuple[] = userIds.map((userId) => ({
      user: `user:${userId}`,
      relation: permission,
      object: `document:${documentId}`,
    }));

    await this.client.deleteTuples(tuples);
    console.log(`已取消 ${userIds.length} 个用户对文档 ${documentId} 的访问`);
  }
}

/**
 * 场景 2: 组织层级权限管理
 */
export class OrganizationHierarchy {
  constructor(private client: OpenFGAClient) {}

  /**
   * 创建组织
   */
  async createOrganization(
    orgId: string,
    adminIds: string[],
    memberIds: string[]
  ): Promise<void> {
    const tuples: RelationshipTuple[] = [];

    // 添加管理员
    adminIds.forEach((adminId) => {
      tuples.push({
        user: `user:${adminId}`,
        relation: 'admin',
        object: `organization:${orgId}`,
      });
    });

    // 添加成员
    memberIds.forEach((memberId) => {
      tuples.push({
        user: `user:${memberId}`,
        relation: 'member',
        object: `organization:${orgId}`,
      });
    });

    await this.client.writeTuples(tuples);
    console.log(`组织 ${orgId} 已创建`);
  }

  /**
   * 添加组织成员
   */
  async addMember(orgId: string, userId: string, role: 'admin' | 'member'): Promise<void> {
    await this.client.writeTuples([
      {
        user: `user:${userId}`,
        relation: role,
        object: `organization:${orgId}`,
      },
    ]);

    console.log(`用户 ${userId} 已添加到组织 ${orgId}，角色: ${role}`);
  }

  /**
   * 移除组织成员
   */
  async removeMember(orgId: string, userId: string): Promise<void> {
    // 删除所有角色
    await this.client.deleteTuples([
      {
        user: `user:${userId}`,
        relation: 'admin',
        object: `organization:${orgId}`,
      },
      {
        user: `user:${userId}`,
        relation: 'member',
        object: `organization:${orgId}`,
      },
    ]);

    console.log(`用户 ${userId} 已从组织 ${orgId} 移除`);
  }

  /**
   * 检查用户是否是组织成员
   */
  async isMember(orgId: string, userId: string): Promise<boolean> {
    return await this.client.check(
      `user:${userId}`,
      'member',
      `organization:${orgId}`
    );
  }

  /**
   * 检查用户是否是组织管理员
   */
  async isAdmin(orgId: string, userId: string): Promise<boolean> {
    return await this.client.check(
      `user:${userId}`,
      'admin',
      `organization:${orgId}`
    );
  }
}

/**
 * 场景 3: 文件夹层级权限
 */
export class FolderHierarchy {
  constructor(private client: OpenFGAClient) {}

  /**
   * 创建文件夹
   */
  async createFolder(
    folderId: string,
    ownerId: string,
    parentFolderId?: string
  ): Promise<void> {
    const tuples: RelationshipTuple[] = [
      {
        user: `user:${ownerId}`,
        relation: 'owner',
        object: `folder:${folderId}`,
      },
    ];

    // 如果有父文件夹，建立父子关系
    if (parentFolderId) {
      tuples.push({
        user: `folder:${parentFolderId}`,
        relation: 'parent',
        object: `folder:${folderId}`,
      });
    }

    await this.client.writeTuples(tuples);
    console.log(`文件夹 ${folderId} 已创建`);
  }

  /**
   * 将文档放入文件夹
   */
  async addDocumentToFolder(documentId: string, folderId: string): Promise<void> {
    await this.client.writeTuples([
      {
        user: `folder:${folderId}`,
        relation: 'parent',
        object: `document:${documentId}`,
      },
    ]);

    console.log(`文档 ${documentId} 已添加到文件夹 ${folderId}`);
  }

  /**
   * 检查用户是否可以访问文件夹
   */
  async canAccessFolder(
    userId: string,
    folderId: string,
    action: 'viewer' | 'editor'
  ): Promise<boolean> {
    return await this.client.check(
      `user:${userId}`,
      action,
      `folder:${folderId}`
    );
  }
}

/**
 * 场景 4: 权限审计
 */
export class PermissionAuditor {
  constructor(private client: OpenFGAClient) {}

  /**
   * 获取用户的所有权限
   */
  async getUserPermissions(userId: string): Promise<{
    documents: string[];
    folders: string[];
    organizations: string[];
  }> {
    const [documents, folders, organizations] = await Promise.all([
      this.client.listObjects(`user:${userId}`, 'viewer', 'document'),
      this.client.listObjects(`user:${userId}`, 'viewer', 'folder'),
      this.client.listObjects(`user:${userId}`, 'member', 'organization'),
    ]);

    return {
      documents: documents.map((d) => d.replace('document:', '')),
      folders: folders.map((f) => f.replace('folder:', '')),
      organizations: organizations.map((o) => o.replace('organization:', '')),
    };
  }

  /**
   * 获取对象的所有访问者
   */
  async getObjectViewers(
    objectType: string,
    objectId: string
  ): Promise<string[]> {
    const response = await this.client.listUsers(
      objectType,
      objectId,
      'viewer',
      [{ type: 'user' }]
    );

    const viewers: string[] = [];
    response.users?.forEach((user) => {
      if (user.object) {
        viewers.push(`${user.object.type}:${user.object.id}`);
      }
    });

    return viewers;
  }

  /**
   * 批量检查用户权限
   */
  async batchCheckUserPermissions(
    userId: string,
    checks: Array<{ objectType: string; objectId: string; relation: string }>
  ): Promise<Map<string, boolean>> {
    const batchChecks = checks.map((check) => ({
      user: `user:${userId}`,
      relation: check.relation,
      object: `${check.objectType}:${check.objectId}`,
      correlationId: `${check.objectType}:${check.objectId}:${check.relation}`,
    }));

    const result = await this.client.batchCheck(batchChecks);

    const permissions = new Map<string, boolean>();
    result.result?.forEach((item) => {
      if (item.correlationId) {
        permissions.set(item.correlationId, item.allowed);
      }
    });

    return permissions;
  }

  /**
   * 生成权限报告
   */
  async generatePermissionReport(userId: string): Promise<void> {
    console.log('='.repeat(60));
    console.log(`用户 ${userId} 的权限报告`);
    console.log('='.repeat(60));

    const permissions = await this.getUserPermissions(userId);

    console.log('\n可访问的文档:');
    permissions.documents.forEach((doc) => console.log(`  - ${doc}`));

    console.log('\n可访问的文件夹:');
    permissions.folders.forEach((folder) => console.log(`  - ${folder}`));

    console.log('\n所属组织:');
    permissions.organizations.forEach((org) => console.log(`  - ${org}`));

    console.log('\n' + '='.repeat(60));
  }
}

/**
 * 运行高级示例
 */
async function runAdvancedExamples() {
  console.log('='.repeat(60));
  console.log('OpenFGA 高级使用场景示例');
  console.log('='.repeat(60));
  console.log();

  const client = new OpenFGAClient();

  // 场景 1: 多租户文档管理
  console.log('场景 1: 多租户文档管理');
  console.log('-'.repeat(60));
  const docSystem = new MultiTenantDocumentSystem(client);

  await docSystem.createDocument(
    'tenant-1',
    'doc-1',
    'alice',
    ['bob', 'charlie'],
    ['bob']
  );

  const aliceCanView = await docSystem.canAccessDocument('alice', 'doc-1', 'viewer');
  console.log(`Alice 可以查看文档: ${aliceCanView}`);

  const bobDocs = await docSystem.getUserDocuments('bob', 'viewer');
  console.log(`Bob 可以查看的文档: ${bobDocs.join(', ')}`);

  console.log();

  // 场景 2: 组织层级管理
  console.log('场景 2: 组织层级管理');
  console.log('-'.repeat(60));
  const orgHierarchy = new OrganizationHierarchy(client);

  await orgHierarchy.createOrganization('acme', ['alice'], ['bob', 'charlie']);

  const isAliceAdmin = await orgHierarchy.isAdmin('acme', 'alice');
  console.log(`Alice 是管理员: ${isAliceAdmin}`);

  const isBobMember = await orgHierarchy.isMember('acme', 'bob');
  console.log(`Bob 是成员: ${isBobMember}`);

  console.log();

  // 场景 3: 文件夹层级
  console.log('场景 3: 文件夹层级权限');
  console.log('-'.repeat(60));
  const folderHierarchy = new FolderHierarchy(client);

  await folderHierarchy.createFolder('root', 'alice');
  await folderHierarchy.createFolder('sub', 'alice', 'root');
  await folderHierarchy.addDocumentToFolder('doc-2', 'sub');

  const aliceCanViewFolder = await folderHierarchy.canAccessFolder(
    'alice',
    'sub',
    'viewer'
  );
  console.log(`Alice 可以查看子文件夹: ${aliceCanViewFolder}`);

  console.log();

  // 场景 4: 权限审计
  console.log('场景 4: 权限审计');
  console.log('-'.repeat(60));
  const auditor = new PermissionAuditor(client);

  await auditor.generatePermissionReport('alice');

  console.log();
  console.log('='.repeat(60));
  console.log('高级示例执行完成！');
  console.log('='.repeat(60));
}

// 导出
export { runAdvancedExamples };

// 如果直接运行此文件
if (require.main === module) {
  runAdvancedExamples().catch((error) => {
    console.error('执行失败:', error);
    process.exit(1);
  });
}
