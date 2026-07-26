(function(root,factory){
  'use strict';
  const library=factory();
  if(typeof module==='object'&&module.exports)module.exports=library;
  else if(root)library.install(root);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const RUNTIME_TYPE='PMP_MOUNT_LIFECYCLE_RUNTIME_V1';
  const POLICY=Object.freeze({
    routeAuthority:'current_map_owner',
    allowedMountOwners:Object.freeze(['app_orchestrator_owner','bank_screen_owner']),
    allowedSources:Object.freeze(['current_map_owner','app_orchestrator_owner','bank_screen_owner']),
    maxOperations:256,
    maxEventsPerOperation:64
  });

  function dependencyStatus(contract,legacy){
    return Object.freeze({
      contract_available:!!contract&&typeof contract.createRegistry==='function'&&
        typeof contract.createLegacyAtlasFacade==='function',
      legacy_atlas_available:!!legacy&&typeof legacy.registry==='function'&&
        typeof legacy.snapshot==='function'&&typeof legacy.scan==='function'
    });
  }
  function rejectOwnerEvent(){
    return Object.freeze({
      accepted:false,
      mutated:false,
      code:'REJECTED_LIFECYCLE_RUNTIME_UNAVAILABLE',
      registry_owner:'mount_registry_owner'
    });
  }
  function unavailable(status){
    return Object.freeze({
      runtimeType:RUNTIME_TYPE,
      version:VERSION,
      available:false,
      mode:'FAIL_CLOSED_NO_PARTIAL_REGISTRY',
      policy:POLICY,
      dependencyStatus:status,
      applyOwnerEvent:rejectOwnerEvent,
      lifecycleSnapshot:()=>null,
      lifecycleOperation:()=>null,
      legacyCompatibility:null,
      sideEffects:Object.freeze({
        automaticLifecycleEvents:0,
        legacyAtlasCalls:0,
        storageMigrations:0,
        routeAssignments:0,
        persistedUserDataWrites:0
      })
    });
  }
  function createRuntime(contract,legacy){
    const status=dependencyStatus(contract,legacy);
    if(!status.contract_available||!status.legacy_atlas_available)return unavailable(status);
    const registry=contract.createRegistry(POLICY);
    const compatibility=contract.createLegacyAtlasFacade(legacy,registry);
    function applyOwnerEvent(event){return registry.apply(event)}
    return Object.freeze({
      runtimeType:RUNTIME_TYPE,
      version:VERSION,
      available:true,
      mode:'PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY',
      contractVersion:contract.contractVersion,
      registryOwner:contract.registryOwner,
      policy:POLICY,
      dependencyStatus:status,
      applyOwnerEvent,
      lifecycleSnapshot:registry.snapshot,
      lifecycleOperation:registry.operation,
      legacyCompatibility:compatibility,
      sideEffects:Object.freeze({
        automaticLifecycleEvents:0,
        legacyAtlasCalls:0,
        storageMigrations:0,
        routeAssignments:0,
        persistedUserDataWrites:0
      })
    });
  }
  function install(target){
    const host=target&&typeof target==='object'?target:null;
    if(!host)return unavailable(dependencyStatus(null,null));
    const existing=host.PMPMountLifecycleRuntimeV1;
    if(existing&&existing.runtimeType===RUNTIME_TYPE)return existing;
    const runtime=createRuntime(host.PMPMountLifecycleContractV1,host.PMPMountRegistryV1);
    host.PMPMountLifecycleRuntimeV1=runtime;
    if(runtime.available)host.PMPMountRegistryLifecycleCompatibilityV1=runtime.legacyCompatibility;
    return runtime;
  }

  return Object.freeze({
    version:VERSION,
    runtimeType:RUNTIME_TYPE,
    policy:POLICY,
    createRuntime,
    install
  });
});
