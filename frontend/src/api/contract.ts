import type { paths } from "./generated/openapi";
import { request } from "./client";

type HttpMethod = "get" | "post" | "put" | "patch" | "delete";
type MethodForPath<P extends keyof paths> = {
  [M in HttpMethod]: NonNullable<paths[P][M]> extends never ? never : M;
}[HttpMethod];
type Operation<P extends keyof paths, M extends HttpMethod> = NonNullable<paths[P][M]>;
type OperationParameters<Op> = Op extends { parameters: infer Parameters }
  ? Parameters
  : {};
type PathParameters<Op> = OperationParameters<Op> extends {
  path?: infer Parameters;
}
  ? NonNullable<Parameters>
  : never;
type QueryParameters<Op> = OperationParameters<Op> extends {
  query?: infer Parameters;
}
  ? NonNullable<Parameters>
  : never;
type JsonRequestBody<Op> = Op extends {
  requestBody: { content: { "application/json": infer Body } };
}
  ? Body
  : never;
type MultipartRequestBody<Op> = Op extends {
  requestBody: { content: { "multipart/form-data": unknown } };
}
  ? FormData
  : never;
type SuccessResponseBody<Responses> = {
  [Status in keyof Responses]: Status extends
    | 200
    | 201
    | 202
    | 203
    | 204
    | 205
    | 206
    | 207
    | 208
    | 226
    ? Responses[Status] extends {
        content: { "application/json": infer Body };
      }
      ? Body
      : never
    : never;
}[keyof Responses];
type JsonResponse<Op> = Op extends { responses: infer Responses }
  ? [SuccessResponseBody<Responses>] extends [never]
    ? unknown
    : SuccessResponseBody<Responses>
  : unknown;
type OptionalParameter<Key extends string, Value> = [Value] extends [never]
  ? { [K in Key]?: never }
  : { [K in Key]: Value };
type OptionalObject<Key extends string, Value> = [Value] extends [never]
  ? { [K in Key]?: never }
  : { [K in Key]?: Value };
type RequestOptions<Op> = Omit<RequestInit, "method" | "body"> &
  OptionalParameter<"pathParams", PathParameters<Op>> &
  OptionalObject<"query", QueryParameters<Op>> &
  ([JsonRequestBody<Op>] extends [never]
    ? { data?: never }
    : { data: JsonRequestBody<Op> }) &
  ([MultipartRequestBody<Op>] extends [never]
    ? { body?: never }
    : { body: MultipartRequestBody<Op> });

function fillPath<P extends string>(
  path: P,
  pathParams: Record<string, string | number> | undefined,
): string {
  return path.replace(/\{([^}]+)\}/g, (_placeholder, name: string) => {
    const value = pathParams?.[name];
    if (value === undefined) {
      throw new Error(`Missing path parameter: ${name}`);
    }
    return encodeURIComponent(String(value));
  });
}

function appendQuery(
  path: string,
  query: Record<string, unknown> | undefined,
): string {
  if (!query) return path;
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue;
    for (const item of Array.isArray(value) ? value : [value]) {
      searchParams.append(key, String(item));
    }
  }
  const serialized = searchParams.toString();
  return serialized ? `${path}?${serialized}` : path;
}

export async function contractRequest<
  const P extends keyof paths,
  M extends MethodForPath<P>,
>(
  path: P,
  method: M,
  options: RequestOptions<Operation<P, M>>,
  token?: string | null,
): Promise<JsonResponse<Operation<P, M>>> {
  const { data, body, pathParams, query, ...requestOptions } = options as RequestOptions<
    Operation<P, M>
  > & {
    data?: unknown;
    body?: BodyInit;
    pathParams?: Record<string, string | number>;
    query?: Record<string, unknown>;
  };
  const resolvedPath = appendQuery(fillPath(path, pathParams), query);
  return request<JsonResponse<Operation<P, M>>>(
    resolvedPath,
    {
      ...requestOptions,
      method: method.toUpperCase(),
      body: body ?? (data === undefined ? undefined : JSON.stringify(data)),
    },
    token,
  );
}
