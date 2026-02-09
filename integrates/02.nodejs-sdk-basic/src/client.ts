import { OpenFgaClient } from '@openfga/sdk';
import type {
  TupleKey,
  CheckRequest,
  CheckResponse,
  BatchCheckRequest,
  BatchCheckResponse,
  ListObjectsRequest,
  ListObjectsResponse,
  ListUsersRequest,
  ListUsersResponse,
  ReadRequest,
  ReadResponse,
  WriteRequest,
} from '@openfga/sdk';
import * as dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

/**
 * OpenFGA 客户端配置接口
 */
export interface OpenFGAClientConfig {
  apiUrl: string;
  storeId?: string;
  authorizationModelId?: string;
}

/**
 * 关系元组接口
 */
export interface RelationshipTuple {
  user: string;
  relation: string;
  object: string;
}

/**
 * 批量检查项接口
 */
export interface BatchCheckItem {
  user: string;
  relation: string;
  object: string;
  context?: Record<string, any>;
  correlationId?: string;
}

/**
 * OpenFGA 客户端封装类
 * 提供简化的 API 用于与 OpenFGA 服务器交互
 */
export class OpenFGAClient {
  private client: OpenFgaClient;
  private config: OpenFGAClientConfig;

  /**
   * 构造函数
   * @param config 客户端配置
   */
  constructor(config?: Partial<OpenFGAClientConfig>) {
    // 从环境变量或配置参数中获取配置
    this.config = {
      apiUrl: config?.apiUrl || process.env.FGA_API_URL || 'http://localhost:8080',
      storeId: config?.storeId || process.env.FGA_STORE_ID,
      authorizationModelId: config?.authorizationModelId || process.env.FGA_MODEL_ID,
    };

    // 初始化 OpenFGA 客户端
    // 建议在应用程序中只初始化一次客户端并重复使用，以提高效率和连接池管理
    this.client = new OpenFgaClient({
      apiUrl: this.config.apiUrl,
      storeId: this.config.storeId,
      authorizationModelId: this.config.authorizationModelId,
    });

    console.log('OpenFGA 客户端已初始化');
    console.log(`API URL: ${this.config.apiUrl}`);
    if (this.config.storeId) {
      console.log(`Store ID: ${this.config.storeId}`);
    }
    if (this.config.authorizationModelId) {
      console.log(`Authorization Model ID: ${this.config.authorizationModelId}`);
    }
  }

  /**
   * 获取原始客户端实例
   * @returns OpenFgaClient 实例
   */
  public getClient(): OpenFgaClient {
    return this.client;
  }

  /**
   * 写入关系元组
   * @param tuples 要写入的关系元组数组
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<void>
   */
  async writeTuples(
    tuples: RelationshipTuple[],
    authorizationModelId?: string
  ): Promise<void> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      await this.client.write(
        {
          writes: tuples,
        },
        options
      );

      console.log(`成功写入 ${tuples.length} 个关系元组`);
    } catch (error) {
      console.error('写入关系元组失败:', error);
      throw new Error(`写入关系元组失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 删除关系元组
   * @param tuples 要删除的关系元组数组
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<void>
   */
  async deleteTuples(
    tuples: RelationshipTuple[],
    authorizationModelId?: string
  ): Promise<void> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      await this.client.write(
        {
          deletes: tuples,
        },
        options
      );

      console.log(`成功删除 ${tuples.length} 个关系元组`);
    } catch (error) {
      console.error('删除关系元组失败:', error);
      throw new Error(`删除关系元组失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 同时写入和删除关系元组（事务模式）
   * @param writes 要写入的关系元组数组
   * @param deletes 要删除的关系元组数组
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<void>
   */
  async writeAndDeleteTuples(
    writes: RelationshipTuple[],
    deletes: RelationshipTuple[],
    authorizationModelId?: string
  ): Promise<void> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      await this.client.write(
        {
          writes,
          deletes,
        },
        options
      );

      console.log(`成功写入 ${writes.length} 个关系元组，删除 ${deletes.length} 个关系元组`);
    } catch (error) {
      console.error('写入/删除关系元组失败:', error);
      throw new Error(`写入/删除关系元组失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 检查用户是否有权限
   * @param user 用户标识符 (例如: "user:alice")
   * @param relation 关系名称 (例如: "viewer")
   * @param object 对象标识符 (例如: "document:mydoc")
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<boolean> 是否有权限
   */
  async check(
    user: string,
    relation: string,
    object: string,
    authorizationModelId?: string
  ): Promise<boolean> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      const response = await this.client.check(
        {
          user,
          relation,
          object,
        },
        options
      );

      return response.allowed;
    } catch (error) {
      console.error('权限检查失败:', error);
      throw new Error(`权限检查失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 批量检查权限（需要 OpenFGA v1.8.0+）
   * @param checks 检查项数组
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<BatchCheckResponse> 批量检查结果
   */
  async batchCheck(
    checks: BatchCheckItem[],
    authorizationModelId?: string
  ): Promise<BatchCheckResponse> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      const response = await this.client.batchCheck(
        {
          checks: checks.map(check => ({
            user: check.user,
            relation: check.relation,
            object: check.object,
            context: check.context,
            correlationId: check.correlationId,
          })),
        },
        options
      );

      return response;
    } catch (error) {
      console.error('批量权限检查失败:', error);
      throw new Error(`批量权限检查失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 列出用户有权限访问的对象
   * @param user 用户标识符
   * @param relation 关系名称
   * @param type 对象类型
   * @param contextualTuples 可选的上下文元组
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<string[]> 对象 ID 数组
   */
  async listObjects(
    user: string,
    relation: string,
    type: string,
    contextualTuples?: RelationshipTuple[],
    authorizationModelId?: string
  ): Promise<string[]> {
    try {
      const options = authorizationModelId ? { authorizationModelId } : {};

      const response = await this.client.listObjects(
        {
          user,
          relation,
          type,
          contextualTuples,
        },
        options
      );

      return response.objects || [];
    } catch (error) {
      console.error('列出对象失败:', error);
      throw new Error(`列出对象失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 列出有权限访问对象的用户
   * @param objectType 对象类型
   * @param objectId 对象 ID
   * @param relation 关系名称
   * @param userFilters 用户过滤器
   * @param contextualTuples 可选的上下文元组
   * @param context 可选的上下文数据
   * @param authorizationModelId 可选的授权模型 ID
   * @returns Promise<ListUsersResponse> 用户列表响应
   */
  async listUsers(
    objectType: string,
    objectId: string,
    relation: string,
    userFilters: Array<{ type: string; relation?: string }>,
    contextualTuples?: RelationshipTuple[],
    context?: Record<string, any>,
    authorizationModelId?: string
  ): Promise<ListUsersResponse> {
    try {
      const options = authorizationModelId ? { authorization_model_id: authorizationModelId } : {};

      const response = await this.client.listUsers(
        {
          object: {
            type: objectType,
            id: objectId,
          },
          relation,
          user_filters: userFilters,
          contextualTuples,
          context,
        },
        options
      );

      return response;
    } catch (error) {
      console.error('列出用户失败:', error);
      throw new Error(`列出用户失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 读取关系元组
   * @param filter 过滤条件
   * @returns Promise<ReadResponse> 读取响应
   */
  async readTuples(filter: Partial<RelationshipTuple>): Promise<ReadResponse> {
    try {
      const response = await this.client.read(filter);
      return response;
    } catch (error) {
      console.error('读取关系元组失败:', error);
      throw new Error(`读取关系元组失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 创建新的 Store
   * @param name Store 名称
   * @returns Promise<string> Store ID
   */
  async createStore(name: string): Promise<string> {
    try {
      const response = await this.client.createStore({ name });
      const storeId = response.id;

      // 更新客户端配置
      this.config.storeId = storeId;
      this.client = new OpenFgaClient({
        apiUrl: this.config.apiUrl,
        storeId: this.config.storeId,
        authorizationModelId: this.config.authorizationModelId,
      });

      console.log(`成功创建 Store: ${storeId}`);
      return storeId;
    } catch (error) {
      console.error('创建 Store 失败:', error);
      throw new Error(`创建 Store 失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 列出所有 Stores
   * @returns Promise<any> Stores 列表
   */
  async listStores(): Promise<any> {
    try {
      const response = await this.client.listStores();
      return response;
    } catch (error) {
      console.error('列出 Stores 失败:', error);
      throw new Error(`列出 Stores 失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 获取当前配置
   * @returns OpenFGAClientConfig
   */
  getConfig(): OpenFGAClientConfig {
    return { ...this.config };
  }

  /**
   * 更新 Store ID
   * @param storeId 新的 Store ID
   */
  setStoreId(storeId: string): void {
    this.config.storeId = storeId;
    this.client = new OpenFgaClient({
      apiUrl: this.config.apiUrl,
      storeId: this.config.storeId,
      authorizationModelId: this.config.authorizationModelId,
    });
    console.log(`Store ID 已更新: ${storeId}`);
  }

  /**
   * 更新授权模型 ID
   * @param authorizationModelId 新的授权模型 ID
   */
  setAuthorizationModelId(authorizationModelId: string): void {
    this.config.authorizationModelId = authorizationModelId;
    this.client = new OpenFgaClient({
      apiUrl: this.config.apiUrl,
      storeId: this.config.storeId,
      authorizationModelId: this.config.authorizationModelId,
    });
    console.log(`Authorization Model ID 已更新: ${authorizationModelId}`);
  }
}

// 导出类型
export type {
  TupleKey,
  CheckRequest,
  CheckResponse,
  BatchCheckRequest,
  BatchCheckResponse,
  ListObjectsRequest,
  ListObjectsResponse,
  ListUsersRequest,
  ListUsersResponse,
  ReadRequest,
  ReadResponse,
  WriteRequest,
};
