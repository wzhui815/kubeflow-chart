
content = '''


    #
    #
    # The old format has the following pattern:
    # ```
    # gateway.{{gateway_namespace}}.{{gateway_name}}: "{{ingress_name}}.{{ingress_namespace}}.svc.cluster.local"
    # ```
    
    # Please use the new configuration format `external-gateways` for future compatibility.
    # This configuration will raise an error if either `external-gateways` or `local-gateways` is defined.


    gateway.knative-serving.knative-ingress-gateway: "istio-ingressgateway.istio-system.svc.cluster.local"


    # local-gateways defines a cluster local gateway to allow pods outside of the mesh to access
    # Services and Routes not exposing through an ingress. If the users
    # do have a service mesh setup, this isn't required and can be removed.
    #
    # An example use case is when users want to use Istio without any
    # sidecar injection (like Knative's istio-ci-no-mesh.yaml). Since every pod
    # is outside of the service mesh in that case, a cluster-local service
    # will need to be exposed to a cluster-local gateway to be accessible.
    #
    # It is the new and preferred way to define the configuration.
    # The format is as follow:
    # ```
    # local-gateways: |
    #   - name: {{local_gateway_name}}
    #     namespace: {{local_gateway_namespace}}
    #     service: {{cluster_local_gateway_name}}.{{cluster_local_gateway_namespace}}.svc.cluster.local
    #     labelSelector:
    #       matchExpressions:
    #       - key: {{label_key}}
    #         operator: {{operator}}
    #         values: [{{label_value}}]
    #       matchLabels:
    #         {{label_key}}: {{label_value}}
    # ```
    # name, namespace & service are mandatory and can't be empty. labelSelector is optional.
    # If labelSelector is specified, the local gateway will be used by the knative service with matching labels.
    # See https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ for more details about labelSelector.
    # Only one local gateway can be specified without a selector. It will act as the default local gateway.
    local-gateways: |
      - name: knative-local-gateway
        namespace: knative-serving
        service: knative-local-gateway.istio-system.svc.cluster.local
    #
    
    #



'''


def wrap_yaml_comments_to_helm(yaml_content: str) -> str:
    """
    修复版：
    1. 连续 # 注释 + 中间空行 → 合并为一个完整 Helm 注释
    2. 注释块 最前 / 最后 的空行不包裹
    3. 注释块 内部空行 保留
    4. 输出格式 {{/* 内容 */}}
    """
    lines = yaml_content.splitlines(keepends=True)
    result = []
    comment_block = []  # 收集当前连续注释块（#行 + 内部空行）

    for line in lines:
        stripped = line.strip()
        is_comment_line = stripped.startswith("#")
        is_blank = stripped == ""

        # ------------------- 核心修复 -------------------
        # 是注释 或 内部空行 → 继续收集到同一个注释块
        if is_comment_line or (is_blank and comment_block):
            comment_block.append(line)
        
        # 不是注释、也不是注释块内部空行 → 结束注释块
        else:
            # 如果有正在收集的注释，先输出
            if comment_block:
                comment_content = "".join(comment_block).rstrip("\n")
                helm_comment = f"{{/*\n{comment_content}\n*/}}"
                result.append(helm_comment + "\n")
                comment_block = []

            # 把当前非注释行加进去（空行 / YAML 内容）
            result.append(line)

    # 处理文件末尾残留的注释块
    if comment_block:
        comment_content = "".join(comment_block).rstrip("\n")
        helm_comment = f"{{/*\n{comment_content}\n*/}}"
        result.append(helm_comment + "\n")

    return "".join(result)


print(wrap_yaml_comments_to_helm(content))
